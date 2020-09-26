import threading
import time
import os
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
    changed = False
    strip = None
    update_frequency = 50

    thread = None
    running = True

    def __init__(self, command_controller):
        self.command_controller = command_controller
        self.create_commands()
        if os.name != 'nt':
            self.init_strip()
        self.init_led_states()
        signal('exit').connect(self.exit)

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

    def init_led_states(self):
        for id in range(self.LED_COUNT):
            self.leds.append({"changed": True, "r": 0, "g": 0, "b": 0})

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

    def run(self):
        print('[led_service] started')
        while self.running:
            changed = False
            for led in self.leds:
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

            time.sleep(1 / self.update_frequency)
        print('[led_service] stopped')

    def exit(self, args=None):
        print('[led_service] exiting...')
        self.running = False

    def set_breath_status(self, breath_status):
        self.breath_status = breath_status

    def set_breath_color(self, breath_color):
        self.breath_color = breath_color

    def set_update_frequency(self, update_frequency):
        self.update_frequency = update_frequency

    def set_led_color(self, id, r=0, g=0, b=0):
        self.leds[id] = {"changed": True, "r": r, "g": g, "b": b}

    def set_all_led_colors(self, r=0, g=0, b=0):
        for id in range(self.LED_COUNT):
            self.set_led_color(r, g, b)

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

    def handle_led_command(self, args=None):
        print(args)
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
