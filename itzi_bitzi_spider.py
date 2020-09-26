#!/usr/bin/python3

import pinject
import time
from blinker import signal

import command_controller
import switch_service
import led_service
# import servo_service
import exit_command
import help_command


class ItziBitziSpider:

    running = True

    def __init__(
        self,
        command_controller,
        switch_service,
        led_service,
        # servo_service,
        exit_command,
        help_command
    ):
        self.command_controller = command_controller
        self.switch_service = switch_service
        self.led_service = led_service
        # self.servo_service = servo_service
        self.exit_command = exit_command
        self.help_command = help_command
        signal('exit').connect(self.exit)

    def run(self):
        print('[main] started')
        while self.running:
            time.sleep(0.1)
        print('[main] stopped')

    def init(self):
        print('[main] parsing command line arguments')
        self.command_controller.parse_sys_args()
        print('[main] creating threads...')
        self.command_controller.create_thread()
        self.switch_service.create_thread()
        self.led_service.create_thread()

    def start_threads(self):
        print('[main] starting threads...')
        self.command_controller.start()
        self.switch_service.start()
        self.led_service.start()

    def join_threads(self):
        print('[main] waiting for remaining threads...')
        self.led_service.join()
        self.switch_service.join()
        self.command_controller.join()

    def shutdown(self):
        print('[main] shutdown completed')

    def exit(self, args=None):
        print('[main] exiting...')
        self.running = False


if __name__ == '__main__':
    obj_graph = pinject.new_object_graph()
    itzi_bitzi_spider = obj_graph.provide(ItziBitziSpider)
    itzi_bitzi_spider.init()
    itzi_bitzi_spider.start_threads()
    itzi_bitzi_spider.run()
    itzi_bitzi_spider.join_threads()
    itzi_bitzi_spider.shutdown()
