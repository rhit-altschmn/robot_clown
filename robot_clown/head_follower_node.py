#!/usr/bin/env python3


# teest code from google 



import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PointStamped
import tf2_ros
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

class HeadTracker(Node):
    def __init__(self):
        super().__init__('head_tracker')
        
        # TF listener to find where the hand is relative to the head
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        
        # Publisher for head joint commands
        self.head_pub = self.create_publisher(
            JointTrajectory, 
            '/stretch_head_controller/joint_trajectory', 
            10
        )
        
        # Timer to run tracking loop at 20 Hz
        self.timer = self.create_timer(0.05, self.track_end_effector)

    def track_end_effector(self):
        try:
            # Look up transform from base_link (or head_pan_link) to the gripper
            now = rclpy.time.Time()
            transform = self.tf_buffer.lookup_transform(
                'camera_color_frame',     # Source frame (Head Camera)
                'link_aruco_top_wrist',           # Target frame (End Effector)
                now
            )
            
            # Extract translations
            dx = transform.transform.translation.x
            dy = transform.transform.translation.y
            dz = transform.transform.translation.z
            
            # Calculate required pan and tilt angles geometrically
            import math
            target_pan = math.atan2(dy, dx)
            target_tilt = math.atan2(-dz, math.sqrt(dx**2 + dy**2))
            
            # Publish command to the head joints
            msg = JointTrajectory()
            msg.joint_names = ['joint_head_pan', 'joint_head_tilt']
            
            point = JointTrajectoryPoint()
            point.positions = [target_pan, target_tilt]
            point.time_from_start.sec = 0
            point.time_from_start.nanosec = int(50 * 1e6) # Smooth 50ms interpolation
            
            msg.points.append(point)
            self.head_pub.publish(msg)

        except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
            # Transform might not be ready at startup
            pass

def main(args=None):
    rclpy.init(args=args)
    node = HeadTracker()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
