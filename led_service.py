import threading
import time
import os
from math import sin, fabs
from blinker import signal
if os.name != 'nt':
    from rpi_ws281x import Adafruit_NeoPixel, Color


class LedService:

    # Number of LED pixels.
    LED_COUNT = 16

    # GPIO pin connected to the pixels (18 uses PWM!).
    LED_PIN = 12

    # LED signal frequency in hertz (usually 800khz)
    LED_FREQ_HZ = 800000

    # DMA channel to use for generating signal (try 10)
    LED_DMA = 10

    # Set to 0 for darkest and 255 for brightest
    LED_BRIGHTNESS = 255

    # True to invert the signal (when using NPN transistor level shift)
    LED_INVERT = False

    # set to '1' for GPIOs 13, 19, 41, 45 or 53
    LED_CHANNEL = 0

    leds = []
    breath = []
    changed = False
    strip = None
    update_frequency = 50

    is_breathing = False
    breath_time_factor = 8

    thread = None
    running = True

    def __init__(self, command_controller):
        self.command_controller = command_controller
        self.create_commands()
        if os.name != 'nt':
            self.init_strip()
        self.init_led_states()
        signal('exit').connect(self.exit)
        signal('diag').send(self, name='led_service', state='starting')

    def create_commands(self):
        parser = self.command_controller.create_command(
            'led',
            'Control the LED',
            self.handle_led_command
        )
        parser.add_argument('--id', type=int, default=-1, help='The change affects to the given led')
        parser.add_argument('--red', type=int, help='Changes the red value')
        parser.add_argument('--green', type=int, help='Changes the green value')
        parser.add_argument('--blue', type=int, help='Changes the blue value')
        parser.add_argument('--is-breathing', type=self.str_to_bool, help='Breathing')
        parser.add_argument('--breath_time_factor', type=int, help='Sets the breath time factor')

    def str_to_bool(self, value):
        if isinstance(value, bool):
            return value
        if value.lower() in {'false', 'f', '0', 'no', 'n', 'off'}:
            return False
        elif value.lower() in {'true', 't', '1', 'yes', 'y', 'on'}:
            return True
        raise ValueError(f'{value} is not a valid boolean value')

    def init_led_states(self):
        self.breath.append([])
        self.breath.append([])
        for id in range(self.LED_COUNT):
            self.leds.append({"changed": True, "r": 0, "g": 0, "b": 0})
            self.breath[0].append({"r": 255, "g": 35, "b": 70})
            self.breath[1].append({"r": 35, "g": 70, "b": 255})

    def init_strip(self):
        # Create NeoPixel object with appropriate configuration.
        self.strip = Adafruit_NeoPixel(
            self.LED_COUNT,
            self.LED_PIN,
            self.LED_FREQ_HZ,
            self.LED_DMA,
            self.LED_INVERT,
            self.LED_BRIGHTNESS,
            self.LED_CHANNEL
        )
        # Initialize the library (must be called once before other functions)
        self.strip.begin()

    def create_thread(self):
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def step(self):
        changed = False
        if self.is_breathing:
            self.calc_breath()
        for id in range(self.LED_COUNT):
            led = self.leds[id]
            if led['changed']:
                if self.strip is not None:
                    self.strip.setPixelColor(
                        id,
                        Color(led['r'], led['g'], led['b'])
                    )
                changed = True
                led['changed'] = False
        if changed:
            if self.strip is not None:
                self.strip.show()
            else:
                print('[led_service] updated')

    def run(self):
        print('[led_service] started')
        signal('diag').send(self, name='led_service', state='started')
        while self.running:
            self.step()
            time.sleep(1 / self.update_frequency)
        print('[led_service] stopped')
        signal('diag').send(self, name='led_service', state='stopping')

    def exit(self, args=None):
        print('[led_service] exiting...')
        self.running = False

    def set_update_frequency(self, update_frequency):
        self.update_frequency = update_frequency

    def set_led_color(self, id, r=0, g=0, b=0):
        self.leds[id] = {"changed": True, "r": r, "g": g, "b": b}

    def set_all_led_colors(self, r=0, g=0, b=0):
        for id in range(self.LED_COUNT):
            self.set_led_color(id, r, g, b)

    def color(self, id=-1, r=0, g=0, b=0):
        if id >= 0:
            self.set_led_color(r, g, b)
        else:
            self.set_all_led_colors(r, g, b)

    def black(self, id=-1):
        self.color(id)

    def white(self, id=-1):
        self.color(id, 255, 255, 255)

    def blue(self, id=-1):
        self.color(id, 255, 0, 0)

    def sine_between(self, min, max, t):
        _min = min
        _max = max
        if min > max:
            _min = max
            _max = min
        halfRange = (_max - _min) / 2.0
        return int(round(_min + halfRange + sin(t) * halfRange))

    def calc_breath(self):
        t = time.time() * self.breath_time_factor
        for id in range(self.LED_COUNT):
            led = self.leds[id]
            breath_min = self.breath[0][id]
            breath_max = self.breath[1][id]
            led['r'] = self.sine_between(breath_min['r'], breath_max['r'], t)
            led['g'] = self.sine_between(breath_min['g'], breath_max['g'], t)
            led['b'] = self.sine_between(breath_min['b'], breath_max['b'], t)
            led['changed'] = True
            print('[breath] %3d %3d %3d' %(led['r'], led['r'], led['r']))

    def handle_led_command(self, args=None):
        print(args)
        if args.red is not None or args.green is not None or args.green is not None:
            if args.id >= 0:
                if args.red is not None and 0 <= args.red <= 255:
                    self.leds[args.id]['r'] = args.red
                if args.green is not None and 0 <= args.green <= 255:
                    self.leds[args.id]['g'] = args.green
                if args.blue is not None and 0 <= args.blue <= 255:
                    self.leds[args.id]['b'] = args.blue
                self.leds[args.id]['changed'] = True
            else:
                for id in range(self.LED_COUNT):
                    if args.red is not None and 0 <= args.red <= 255:
                        self.leds[id]['r'] = args.red
                    if args.green is not None and 0 <= args.green <= 255:
                        self.leds[id]['g'] = args.green
                    if args.blue is not None and 0 <= args.blue <= 255:
                        self.leds[id]['b'] = args.blue
                    self.leds[id]['changed'] = True
        if args.is_breathing is not None:
            self.is_breathing = args.is_breathing
        if args.breath_time_factor is not None:
            self.breath_time_factor = args.breath_time_factor
