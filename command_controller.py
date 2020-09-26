import argparse
import sys
import threading
import traceback
from blinker import signal
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
# from prompt_toolkit.completion import FuzzyCompleter, FuzzyWordCompleter


class CommandController():

    parser = None
    subparsers_command = None
    args = None
    commands = {}

    thread = None
    running = True

    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Itzi Bitzi Spider')
        self.subparsers_command = self.parser.add_subparsers(dest='command')
        signal('exit').connect(self.exit)

    def create_thread(self):
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def create_command(self, command_name, help, callback):
        self.commands[command_name] = callback
        print('[command_controller] created command %s' % command_name)
        return self.subparsers_command.add_parser(
            command_name,
            help=help
        )

    def parse_sys_args(self):
        self.args = self.parser.parse_args()

    def parse_user_input(self, user_input):
        return self.parser.parse_args(user_input)

    def execute_user_input(self, user_input):
        try:
            print(user_input)
            print(user_input.split())
            args = None
            try:
                args = self.parse_user_input(user_input.split())
            except SystemExit:
                pass
            print(args)
            if args is not None and args.command in self.commands:
                try:
                    self.commands[args.command](args)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
            else:
                print("[command_controller] command not found")
        except argparse.ArgumentError as e:
            print(e)

    def run(self):
        print('[command_controller] started')
        while self.running:
            try:
                user_input = prompt(
                    '>',
                    history=FileHistory('history.txt'),
                    auto_suggest=AutoSuggestFromHistory()
                )
                self.execute_user_input(user_input)
            except KeyboardInterrupt:
                print('[command_controller] sending exit signal...')
                signal('exit').send(self)
        print('[command_controller] stopped')

    def exit(self, args=None):
        print('[command_controller] exiting...')
        self.running = False

    def help(self, args=None):
        self.parser.print_help()


if __name__ == '__main__':
    command_controller = CommandController()
    command_controller.parse_sys_args()
    command_controller.create_command('exit', '', command_controller.exit)
    command_controller.create_command('help', '', command_controller.help)
    command_controller.create_thread()
    command_controller.start()
    command_controller.join()
