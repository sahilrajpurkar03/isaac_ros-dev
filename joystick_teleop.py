#!/usr/bin/env python3
"""Drive the robot in Isaac Sim with a game controller (publishes /cmd_vel).

Run inside the Isaac ROS container. Needs: pip3 install pygame
Axes and speeds are ROS parameters, so you can change them without editing the file:
    python3 joystick_teleop.py --ros-args -p linear_axis:=1 -p angular_axis:=3 -p max_linear:=0.5 -p max_angular:=1.0
Find your axis numbers with:  python3 joystick_teleop.py --ros-args -p print_axes:=true
"""
import os
import threading
import time

# no display and no sound card needed, only the joystick
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
# inside Docker, SDL does not auto-detect the controller (no udev database), so point it at the device.
# Change js0 to js1 etc. if you have several controllers: ls /dev/input
os.environ.setdefault('SDL_JOYSTICK_DEVICE', '/dev/input/js0')

import pygame
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class JoystickTeleop(Node):
    def __init__(self):
        super().__init__('joystick_teleop')

        self.declare_parameter('linear_axis', 1)       # left stick up/down
        self.declare_parameter('angular_axis', 3)      # right stick left/right
        self.declare_parameter('max_linear', 0.5)      # m/s at full stick
        self.declare_parameter('max_angular', 1.0)     # rad/s at full stick
        self.declare_parameter('deadzone', 0.05)
        self.declare_parameter('print_axes', False)
        self.declare_parameter('rate_hz', 20.0)

        self.linear_axis = self.get_parameter('linear_axis').value
        self.angular_axis = self.get_parameter('angular_axis').value
        self.max_linear = self.get_parameter('max_linear').value
        self.max_angular = self.get_parameter('max_angular').value
        self.deadzone = self.get_parameter('deadzone').value
        self.print_axes = self.get_parameter('print_axes').value
        self.period = 1.0 / self.get_parameter('rate_hz').value

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            self.get_logger().error(
                'No joystick found. Connect it, and check that the container can see it: ls /dev/input')
            raise SystemExit(1)

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.get_logger().info(
            f'Joystick: {self.joystick.get_name()} ({self.joystick.get_numaxes()} axes). '
            f'Linear axis {self.linear_axis}, angular axis {self.angular_axis}')

        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def dz(self, value):
        return 0.0 if abs(value) < self.deadzone else value

    def loop(self):
        while self.running:
            pygame.event.pump()

            if self.print_axes:
                axes = [round(self.joystick.get_axis(i), 2) for i in range(self.joystick.get_numaxes())]
                print(f'axes: {axes}', end='\r', flush=True)
                time.sleep(self.period)
                continue

            # stick up is negative on most controllers, so flip it
            forward = self.dz(-self.joystick.get_axis(self.linear_axis))
            turn = self.dz(-self.joystick.get_axis(self.angular_axis))  # stick left = turn left

            msg = Twist()
            msg.linear.x = forward * self.max_linear
            msg.angular.z = turn * self.max_angular
            self.pub.publish(msg)
            time.sleep(self.period)

    def stop(self):
        self.running = False
        self.thread.join(timeout=1.0)
        self.pub.publish(Twist())  # zero velocity so the robot stops
        pygame.quit()


def main():
    rclpy.init()
    node = JoystickTeleop()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
