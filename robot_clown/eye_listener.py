#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray
import serial
import numpy as np

class EyeListenerNode(Node):

    def __init__(self):
        super().__init__('eye_listener')
        
        # Configure the serial port
        self.serial_port = serial.Serial('/dev/ttyACM2', baudrate=57600, timeout=1)
        
        # Create the subscriber
        self.cam_sub = self.create_subscription(JointState,'/stretch/joint_states', self.joint_states_callback,10)
        self.key_sub = self.create_subscription(String,'/keyboard_driver', self.keyboard_callback,5)

        self.key = '-'
        self.horiz = None
        self.vert = None

        self.eye_loc = 25
        self.pupil_loc = 25
        
        self.ser_msgs = '-'

        upper_limit = 0.415
        lower_limit = -1.917

        left_limit = 1.73
        right_limit = -4.04


        
        self.eye_edges = np.array([-2.75,-1.96,-1.18,-0.4,0.4,1.18])   #{1.178097245,	0.3926990817,	-0.3926990817,	-1.178097245,	-1.963495408,	-2.748893572}
        self.pupil_vert_edges = np.array([-0.337,0.001,0.139,0.277])  #verticals
        self.pupil_hor_edges = np.array([0.16, 0.32, 0.48, 0.52])  #horizontals

        self.pupil_grid = np.array([[2,2,1,4,4], [2,2,3,4,4], [5,6,7,8,9], [10,10,11,12,12], [10,10,13,12,	12]])


    def joint_states_callback(self, msg):
        # self.get_logger().info(f'Received: "{msg.data}"')
        for i, joint_name in enumerate (msg.name):
            if joint_name == 'joint_head_pan':
                self.horiz = msg.position[i]
            elif joint_name == 'joint_head_tilt':
                self.vert = msg.position[i]

        
        self.find_pupil_loc()
       
        # # Send data out over the serial port (requires encoding)
        # self.serial_port.write((msg.data + '\n').encode('utf-8'))

    
    def keyboard_callback(self, msg):
        self.get_logger().info(f'Received Key: "{msg.data}"')


    def camPanMap(self):
        #int eye_index = 0;
        for i in range (6):
            if(self.horiz < self.eye_edges[i]):
                return i
            
        return 5

    def camTiltMap(self):
        
        for j in range (5):
            if self.vert < self.pupil_vert_edges[j]:
                return j
             
        return 4
    
    def find_pupil_loc(self):
        self.eye_loc = self.camPanMap()

        pup_vert = self.camTiltMap()

        pup_horiz = 10

        eye_bound = self.eye_edges[self.eye_loc]

        for k in range(4):

            if self.horiz < (eye_bound + self.pupil_hor_edges[k]):
                pup_horiz = k
                break
             
        if pup_horiz == 10:
            pup_horiz = 4

        self.pupil_loc = self.pupil_grid[pup_horiz][pup_vert]

        self.get_logger().info(f'Pupil Locations: Horiz {pup_horiz}  Vert: {pup_vert}  Loc: {self.pupil_loc}')
        
        self.ser_msg = f"Eye:{self.eye_loc} Pup:{pup_vert}" 
        self.serial_port.write((self.ser_msg + '\n').encode('utf-8'))
        self.get_logger().info(f'Serial Msg:  {self.ser_msg}')




def main(args=None):
    rclpy.init(args=args)
    node = EyeListenerNode()
    rclpy.spin(node)
    # node.destroy_node()
    # rclpy.shutdown()

if __name__ == '__main__':
    main()
