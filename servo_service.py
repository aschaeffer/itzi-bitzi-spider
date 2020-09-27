import random
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
    sc_angles = [
        0,0,0,0,
        0,0,0,0,
        0,0,0,0,
        0,0,0,0
    ]
    sc_current = [
        0,0,0,0,
        0,0,0,0,
        0,0,0,0,
        0,0,0,0
    ]
    sc_time = [
        0.0,0.0,0.0,0.0,
        0.0,0.0,0.0,0.0,
        0.0,0.0,0.0,0.0,
        0.0,0.0,0.0,0.0
    ]

    sc_gear = None
    sc_frequency = 2
    p_sc = None
    t_sc = None
    init_pwm = []

    thread = None
    running = True

    def __init__(self, command_controller):
        self.command_controller = command_controller
        self.create_servos()
        self.initialize_pwm()
        self.create_commands()
        signal('exit').connect(self.exit)
        signal('diag').send(self, name='servo_service', state='starting')

    def create_servos(self):
        self.sc_gear = ServoCtrl()
        self.sc_gear.moveInit()

        # self.p_sc = ServoCtrl()
        # self.p_sc.start()
        #
        # self.t_sc = ServoCtrl()
        # self.t_sc.start()

    def initialize_pwm(self):
        for i in range(16):
            self.init_pwm.append(self.sc_gear.initPos[i])

    def create_commands(self):
        parser = self.command_controller.create_command(
            'servo',
            'Control the servo',
            self.handle_servo_command
        )
        parser.add_argument('--id', type=int, default=-1, help='The change affects to the given servo')
        parser.add_argument('--angle', type=int, help='The angle')
        parser.add_argument('--time', type=float, default=1.0, help='The angle')

    def create_thread(self):
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

    def run(self):
        signal('diag').send(self, name='servo_service', state='started')
        while self.running:
            # print("[servo_service] run")
            # self.sc_gear.moveAngle(0, random.random() * 40 - 20)
            time_delta = 1.0 / self.sc_frequency
            for id in range(len(self.sc_angles)):
                if self.sc_time[id] > time_delta:
                    total_delta = self.sc_angles[id] - self.sc_current[id]
                    time_steps = self.sc_time[id] / time_delta
                    delta_step = total_delta / time_steps
                    print('%f --- %f %f %f --- %f %f %f' %(
                        time_delta,
                        total_delta, time_steps, delta_step,
                        self.sc_current[id], self.sc_angles[id], self.sc_time[id]
                    ))
                    self.sc_current[id] += delta_step
                    self.sc_angles[id] -= delta_step
                    self.sc_time[id] -= time_delta
                    print('%f %f %f' %(self.sc_current[id], self.sc_angles[id], self.sc_time[id]))
                    if -45 <= delta_step <= 45:
                        # self.sc_gear.moveAngle(id, delta_step)
                        pass
            time.sleep(time_delta)
        print('[servo_service] stopping')
        signal('diag').send(self, name='servo_service', state='stopping')

    def exit(self, args=None):
        print('[servo_service] exiting...')
        self.running = False


    def handle_servo_command(self, args=None):
        print(args)
        if args.angle is not None:
            if args.id >= 0:
                self.sc_angles[args.id] = args.angle
                self.sc_time[args.id] = args.time
            else:
                for id in range(len(self.sc_angles)):
                    self.sc_angles[id] = args.angle
                    self.sc_time[id] = args.time




if __name__ == '__main__':
    servo_service = ServoService()
