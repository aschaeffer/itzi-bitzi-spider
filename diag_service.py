import led_service
from blinker import signal


class DiagService:

    states = {
        'led_service': {
            'starting': {'id': 0, 'r': 0, 'g': 30, 'b': 0},
            'started': {'id': 0, 'r': 0, 'g': 255, 'b': 0},
            'stopping': {'id': 0, 'r': 30, 'g': 0, 'b': 0},
            'stopped': {'id': 0, 'r': 255, 'g': 0, 'b': 0}
        },
        'servo_service': {
            'starting': {'id': 1, 'r': 0, 'g': 30, 'b': 0},
            'started': {'id': 1, 'r': 0, 'g': 255, 'b': 0},
            'stopping': {'id': 1, 'r': 30, 'g': 0, 'b': 0},
            'stopped': {'id': 1, 'r': 255, 'g': 0, 'b': 0}
        }
    }

    def __init__(self, led_service):
        self.led_service = led_service
        signal('diag').connect(self.diag)

    def diag(self, sender, **data):
        print(sender)
        print(data['name'])
        print(data['state'])
        name = data['name']
        state = data['state']
        state = self.states[name][state]
        self.led_service.set_led_color(state['id'], state['b'], state['g'], state['b'])
        self.led_service.step()
