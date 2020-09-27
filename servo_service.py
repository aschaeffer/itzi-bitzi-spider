import threading
import time
from blinker import signal
from server.RPIservo import ServoCtrl


class ServoService:

    sc_direction = [
        1,1,1,1,
        1,1,1,1,
        1,1,1,1,
        1,1,1,1
    ]

    sc_gear = None
    p_sc = None
    t_sc = None
    init_pwm = []

    thread = None
    running = True

    def __init__(self):
        self.create_servos()
        self.initialize_pwm()
        signal('exit').connect(self.exit)
        signal('diag').send(self, name='servo_service', state='starting')

    def create_servos(self):
        self.sc_gear = ServoCtrl()
        self.sc_gear.moveInit()

        self.p_sc = ServoCtrl()
        self.p_sc.start()

        self.t_sc = ServoCtrl()
        self.t_sc.start()

    def initialize_pwm(self):
        for i in range(16):
            self.init_pwm.append(self.sc_gear.initPos[i])

    def create_thread(self):
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        signal('diag').send(self, name='servo_service', state='started')
        while self.running:
            print("[servo_service] run")
            time.sleep(1)
        print('[servo_service] stopping')
        signal('diag').send(self, name='servo_service', state='stopping')

    def exit(self, args=None):
        print('[servo_service] exiting...')
        self.running = False


if __name__ == '__main__':
    servo_service = ServoService()
