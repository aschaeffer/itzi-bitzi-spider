from command_controller import CommandController


class HelpCommand:

    def __init__(self, command_controller):
        command_controller.create_command(
            'help',
            'Prints the help',
            command_controller.help
        )


if __name__ == '__main__':
    command_controller = CommandController()
    exit_command = HelpCommand(command_controller)
    command_controller.execute_user_input('help')
