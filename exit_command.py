from blinker import signal
from command_controller import CommandController


class ExitCommand:

    exit_signal = signal('exit')

    def __init__(self, command_controller):
        command_controller.create_command(
            'exit',
            'Exits program',
            self.send_exit_signal
        )

    def send_exit_signal(self, args=None):
        print('[exit_command] sending exit signal...')
        self.exit_signal.send(self)


if __name__ == '__main__':
    command_controller = CommandController()
    exit_command = ExitCommand(command_controller)
    thread = command_controller.create_thread()
    command_controller.execute_user_input('exit')
