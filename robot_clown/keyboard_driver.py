#!/usr/bin/env python3

import argparse as ap
from functools import partial
import math
import sys
from stretch_core.keyboard import KBHit

import rclpy
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from sensor_msgs.msg import JointState
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint, MultiDOFJointTrajectoryPoint
from geometry_msgs.msg import Transform

import hello_helpers.hello_misc as hm


class GetKeyboardCommands:

    def __init__(self, node):
        self.kb = KBHit()
        
        self.node = node
        self.step_size = 'medium'
        self.rad_per_deg = math.pi/180.0
        self.small_deg = 3.0
        self.small_rad = self.rad_per_deg * self.small_deg
        self.small_translate = 0.005  #0.02
        self.medium_deg = 6.0
        self.medium_rad = self.rad_per_deg * self.medium_deg
        self.medium_translate = 0.04
        self.big_deg = 12.0
        self.big_rad = self.rad_per_deg * self.big_deg
        self.big_translate = 0.06
        self.mode = 'position' #'trajectory' #'navigation'

    def get_deltas(self):
        if self.step_size == 'small':
            deltas = {'rad': self.small_rad, 'translate': self.small_translate}
        if self.step_size == 'medium':
            deltas = {'rad': self.medium_rad, 'translate': self.medium_translate} 
        if self.step_size == 'big':
            deltas = {'rad': self.big_rad, 'translate': self.big_translate} 
        return deltas

    def print_commands(self):
        print('---------- KEYBOARD TELEOP MENU -----------')
        

    def get_command(self, node):
        command = None
        hot_command = None
        c = None

        if self.kb.kbhit(): # Returns True if any key pressed
            c = self.kb.getch()
            
            if c is not None:
                node.publish_keyboard_input(c)


        match c:
            # Base
            case 'w':
                command = {'joint': 'translate_mobile_base', 'inc': self.get_deltas()['translate']}
            case 's':
                command = {'joint': 'translate_mobile_base', 'inc': -self.get_deltas()['translate']}
            case 'a':
                command = {'joint': 'rotate_mobile_base', 'inc': self.get_deltas()['rad']}
            case 'd':
                command = {'joint': 'rotate_mobile_base', 'inc': -self.get_deltas()['rad']}

            # head cam
            case 'f':
                command = {'joint': 'joint_head_tilt', 'delta': (2.0 * self.get_deltas()['rad'])}
            case 'c':
                command = {'joint': 'joint_head_tilt', 'delta': -(2.0 * self.get_deltas()['rad'])}
            case 'x':
                command = {'joint': 'joint_head_pan', 'delta': (2.0 * self.get_deltas()['rad'])}
            case 'v':
                command = {'joint': 'joint_head_pan', 'delta': -(2.0 * self.get_deltas()['rad'])}

            # head cam hot keys
            case 'F':
                command = {'joint': 'joint_head_pan', 'hot': 0.0}
                hot_command = {'joint': 'joint_head_tilt', 'hot': 0.0}
            case 'C':
                command = {'joint': 'joint_head_pan', 'hot': -2.75}
                hot_command = {'joint': 'joint_head_tilt', 'hot': 0.0}
            case 'X':
                command = {'joint': 'joint_head_pan', 'hot': 1}
                hot_command = {'joint': 'joint_head_tilt', 'hot': 0.0}
            case 'V':
                command = {'joint': 'joint_head_pan', 'hot': -1}
                hot_command = {'joint': 'joint_head_tilt', 'hot': 0.0}

            # lift
            case 'h':
                command = {'joint': 'joint_lift', 'delta': self.get_deltas()['translate']}
            case 'n':
                command = {'joint': 'joint_lift', 'delta': -self.get_deltas()['translate']}
            case 'm':
                command = {'joint': 'wrist_extension', 'delta': self.get_deltas()['translate']}
            case 'b':
                command = {'joint': 'wrist_extension', 'delta': -self.get_deltas()['translate']}

            # wrist
            case 'l':
                command = {'joint': 'joint_wrist_yaw', 'delta': -self.get_deltas()['rad']}
            case 'j':
                command = {'joint': 'joint_wrist_yaw', 'delta': self.get_deltas()['rad']}
            case 'k':
                command = {'joint': 'joint_wrist_pitch', 'delta': -self.get_deltas()['rad']}
            case 'i':
                command = {'joint': 'joint_wrist_pitch', 'delta': self.get_deltas()['rad']}
            case 'u':
                command = {'joint': 'joint_wrist_roll', 'delta': -self.get_deltas()['rad']}
            case 'o':
                command = {'joint': 'joint_wrist_roll', 'delta': self.get_deltas()['rad']}

            # gripper
            case '8': #closed
                command = {'joint': 'joint_gripper_finger_left', 'delta': -self.get_deltas()['rad']}
            case '9': #open
                command = {'joint': 'joint_gripper_finger_left', 'delta': self.get_deltas()['rad']}
            
        
        if c == '>':
            node.get_logger().info('process_keyboard.py: changing to BIG step size')
            self.step_size = 'big'
        if c == '?':
            node.get_logger().info('process_keyboard.py: changing to MEDIUM step size')
            self.step_size = 'medium'
        if c == '<':
            node.get_logger().info('process_keyboard.py: changing to SMALL step size')
            self.step_size = 'small'
        
        if c == 'q' or c == 'Q':
            node.get_logger().info('keyboard_teleop exiting...')
            node.get_logger().info('Received quit character (q), so exiting')
            node.destroy_node()
            rclpy.shutdown()
            sys.exit(0)

        ####################################################

        return command,hot_command


class KeyboardDriverNode(Node):

    def __init__(self):
        super().__init__('keyboard_driver')
        

        self.keys = GetKeyboardCommands(self)

        self.keyboard_pub = self.create_publisher(String, '/keyboard_driver', 10)

        self.joint_state = JointState()
        self.robot_mode = String()

        self.arm_lim = False
        self.lift_lim = False
        self.pan_lim = False
        self.tilt_lim = False
        self.wrist_yaw_lim = False  # 330 deg range
        self.wrist_pitch_lim = False
        self.grip_lim = False
        self.error_string = ''
        self.err_count = 0


        
    def joint_states_callback(self, joint_state):
        self.joint_state = joint_state

    def mode_callback(self, mode):
        self.robot_mode = mode.data

    def publish_keyboard_input(self, key_char):
        msg = String()
        msg.data = key_char
        self.keyboard_pub.publish(msg)
        # self.get_logger().info(f'Publishing Key: "{msg.data}"' )

    def find_errors(self):
        # self.error_string = '-'
        err_list = []
        
        if self.arm_lim:
            err_list.append(" Arm Limit ")
        if self.lift_lim:
            err_list.append(" Lift Limit ")
        if self.grip_lim:
            err_list.append(" Grip Limit")
        if self.pan_lim:
            err_list.append(" Cam Pan Limit")
        if self.tilt_lim:
            err_list.append(" Cam Tilt Limit")
        if self.wrist_yaw_lim:
            err_list.append(" Wrist Yaw Limit")
        if self.wrist_pitch_lim:
            err_list.append(" Wrist Pitch Limit")

        if not err_list:
            # self.get_logger().info(f'err count: {self.err_count}')
            self.error_string = "no range errors"
            if self.err_count % 20 == 0:
                self.get_logger().info(f'{self.error_string}')
                # self.err_count = 0
            self.err_count+=1
        else:
            self.error_string = " ".join(err_list)
            self.get_logger().warn(f'Range: {self.error_string}')
            self.err_count = 0


    def send_command(self, command):
        joint_state = self.joint_state
        if (joint_state is not None) and (command is not None):
            if self.robot_mode == 'position':
                point = JointTrajectoryPoint()
                duration = Duration(seconds=0.0)
                point.time_from_start = duration.to_msg()
                trajectory_goal = FollowJointTrajectory.Goal()
                # trajectory_goal.goal_time_tolerance = rclpy.time.Time()
                joint_name = command['joint']
                trajectory_goal.trajectory.joint_names = [joint_name]

                # for base joints
                if 'inc' in command:
                    inc = command['inc']
                    new_value = inc

                # for non-base joints
                elif 'delta' in command:
                    joint_index = joint_state.name.index(joint_name)
                    joint_value = joint_state.position[joint_index]
                    delta = command['delta']
                    new_value = joint_value + delta

                elif 'hot' in command:
                    joint_index = joint_state.name.index(joint_name)
                    # joint_value = joint_state.position[joint_index]
                    delta = command['hot']
                    new_value = delta

                # limit checks
                if joint_name == 'joint_head_tilt':
                    if new_value < -1.3:
                        self.tilt_lim = True
                    elif new_value > 0.4:  #115 deg range
                        self.tilt_lim = True
                    else:
                        self.tilt_lim = False

                if joint_name == 'joint_head_pan':
                    if new_value < -1.6:
                        self.pan_lim = True
                    elif new_value > 6.5: #336 deg range probably radians though
                        self.pan_lim = True
                    else:
                        self.pan_lim = False

                if joint_name == 'joint_lift':
                    if new_value < 0.175:
                        self.lift_lim = True
                        new_value = joint_value
                    elif new_value > 1.0:
                        self.lift_lim = True
                    else:
                        self.lift_lim = False

                if joint_name == 'wrist_extension':
                    if new_value < 0.001:
                        self.arm_lim = True
                    elif new_value > 0.51:           #0.11:
                        self.arm_lim = True
                    else:
                        self.arm_lim = False
                
                if joint_name == 'joint_gripper_finger_left':
                    if new_value < -0.35:
                        self.grip_lim = True
                    elif new_value > 0.61:  
                        self.grip_lim = True
                    else:
                        self.grip_lim = False

                if joint_name == 'joint_wrist_yaw':
                    if new_value < -1.3:
                        self.wrist_yaw_lim = True
                    elif new_value > 4.4: 
                        self.wrist_yaw_lim = True
                    else:
                        self.wrist_yaw_lim = False

                if joint_name == 'joint_wrist_pitch':
                    if new_value < -1.5:
                        self.wrist_pitch_lim = True
                    elif new_value > 0.5: 
                        self.wrist_pitch_lim = True
                    else:
                        self.wrist_pitch_lim = False

                point.positions = [new_value]
                trajectory_goal.trajectory.points = [point]
                self.trajectory_client.send_goal_async(trajectory_goal)

                

            self.find_errors()
            
                    


    def main(self):
        self.trajectory_client = ActionClient(self, FollowJointTrajectory, '/stretch_controller/follow_joint_trajectory')
        server_reached = self.trajectory_client.wait_for_server(timeout_sec=10.0)
        if not server_reached:
            self.get_logger().error('Unable to connect to server. Timeout exceeded. Is stretch_driver running?')
            sys.exit()

        self.joint_states_sub = self.create_subscription(JointState, '/stretch/joint_states', self.joint_states_callback, 1)
        self.joint_states_sub

        self.robot_mode_sub = self.create_subscription(String, 'mode', self.mode_callback, 10)
        self.robot_mode_sub

        self.trajectory_client = ActionClient(self, FollowJointTrajectory, '/stretch_controller/follow_joint_trajectory')
        server_reached = self.trajectory_client.wait_for_server(timeout_sec=60.0)
        if not server_reached:
            self.get_logger().error('Unable to connect to arm action server. Timeout exceeded.')
            sys.exit()

        
        self.keys.print_commands()
        while rclpy.ok():
            rclpy.spin_once(self)
            command,hot_command = self.keys.get_command(self)
            self.send_command(command)
            if hot_command is not None:
                self.send_command(hot_command)

        self.keys.kb.set_normal_term()
        self.destroy_node()
        # rclpy.shutdown()

def main():
    try:
        rclpy.init()
        node = KeyboardDriverNode()
        node.main()
    except KeyboardInterrupt:
        node.get_logger().info('interrupt received, so shutting down')
        rclpy.shutdown()

if __name__ == '__main__':
    main()
