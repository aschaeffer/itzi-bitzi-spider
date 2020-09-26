import RPi.GPIO as GPIO

class SwitchService:

    switch_ids = [ 1, 2, 3 ]
    gpio_pins = [ 5, 6, 13 ]

    def __init__(self):
        self.setup_switches()

    def get_gpio_pin(self, switch_id):
        if 1 <= switch_id <= len(self.gpio_pins):
            return self.gpio_pins[switch_id]
        else:
            raise ValueError("Illegal switch id: %d" % switch_id)

    def get_switch_id(self, gpio_pin):
        return self.gpio_pins.index(gpio_pin) + 1

    def setup_switches(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for gpio_pin in self.gpio_pins:
            GPIO.setup(gpio_pin, GPIO.OUT)

    def set_switch_state(self, gpio_pin, state):
        if state == 1:
            GPIO.output(gpio_pin, GPIO.HIGH)
        elif state == 0:
            GPIO.output(gpio_pin,GPIO.LOW)
        else:
            pass

    def set_switch(self, switch_id, state):
        self.set_switch_state(self.get_gpio_pin(switch_id), state)

    def set_all_switches(self, state):
        for switch_id in range(len(self.gpio_pins)):
            self.set_switch(switch_id, state)

    def set_all_switches_off(self):
        self.set_all_switches(0)

    def set_all_switches_on(self):
        self.set_all_switches(1)

if __name__ == '__main__':
    switch_service = SwitchService()
