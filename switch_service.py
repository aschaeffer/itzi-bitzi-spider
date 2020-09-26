import threading
import time
from blinker import signal
from gpiozero import DigitalOutputDevice
from command_controller import CommandController


class SwitchService:

    switch_ids = [1, 2, 3]
    gpio_pins = [5, 6, 13]
    output_devices = {}

    thread = None
    running = True

    def __init__(self, command_controller):
        self.command_controller = command_controller

        self.mock_gpio()
        self.setup_switches()
        self.create_commands()

        signal('exit').connect(self.exit)

    def mock_gpio(self):
        import os
        if os.name == 'nt':
           print('Mocking GPIOs')
           from gpiozero import Device
           from gpiozero.pins.mock import MockFactory
           Device.pin_factory = MockFactory()

    def setup_switches(self):
        print('Setup switches')
        for gpio_pin in self.gpio_pins:
            self.output_devices[gpio_pin] = DigitalOutputDevice(gpio_pin)

    def create_commands(self):
        parser = self.command_controller.create_command(
            'switch',
            'Sets the state of the switch',
            self.set_switch_parse
        )
        parser.add_argument('--switch-id', type=int, help='The switch ID (numbering starts with 1)')
        parser.add_argument('--gpio', type=int, help='The GPIO port number (BCM)')
        parser.add_argument('--state', type=self.str_to_bool, default=None, help='The state')

    def str_to_bool(self, value):
        if isinstance(value, bool):
            return value
        if value.lower() in {'false', 'f', '0', 'no', 'n', 'off'}:
            return False
        elif value.lower() in {'true', 't', '1', 'yes', 'y', 'on'}:
            return True
        raise ValueError(f'{value} is not a valid boolean value')

    def create_thread(self):
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        print('[switch_service] started')
        while self.running:
            for gpio_pin in self.gpio_pins:
                output_device = self.output_devices[gpio_pin]
                # print('[switch_service] %d %d %d' %(self.get_switch_id(gpio_pin), gpio_pin, output_device.value))
            time.sleep(1)
        print('[switch_service] stopped')

    def exit(self, args=None):
        print('[switch_service] exiting...')
        self.running = False

    def get_gpio_pin(self, switch_id):
        if 1 <= switch_id <= len(self.gpio_pins):
            return self.gpio_pins[switch_id]
        else:
            raise ValueError('Illegal switch id: %d' % switch_id)

    def get_switch_id(self, gpio_pin):
        return self.gpio_pins.index(gpio_pin) + 1

    def set_switch_state(self, gpio_pin, state):
        if state:
            self.output_devices[gpio_pin].on()
        else:
            self.output_devices[gpio_pin].off()

    def get_switch_state(self, gpio_pin):
        return self.output_devices[gpio_pin].value

    def set_switch(self, switch_id, state):
        self.set_switch_state(self.get_gpio_pin(switch_id), state)

    def get_switch(self, switch_id):
        self.get_switch_state(self.get_gpio_pin(switch_id))

    def set_switch_parse(self, args=None):
        print(args)
        if args.switch_id is not None:
            if args.state is not None:
                self.set_switch(args.switch_id, args.state)
            else:
                print(self.get_switch(args.switch_id))
        elif args.gpio is not None:
            if args.state is not None:
                self.set_switch_state(args.gpio, args.state)
            else:
                print(self.get_switch_state(args.gpio))

    def set_all_switches(self, state):
        for switch_id in range(1, len(self.gpio_pins)):
            self.set_switch(switch_id, state)

    def set_all_switches_off(self):
        self.set_all_switches(False)

    def set_all_switches_on(self):
        self.set_all_switches(True)


if __name__ == '__main__':
    command_controller = CommandController()
    switch_service = SwitchService(command_controller)
    import sys
    if len(sys.argv) > 1:
        argv = sys.argv[1:]
        argv.insert(0, 'switch')
        command = ' '.join(argv)
        command_controller.execute_user_input(command)
    else:
        switch_service.set_all_switches_off()
