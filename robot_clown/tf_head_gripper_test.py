import rclpy
from rclpy.node import Node
from rclpy.time import Time

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

import math


# This node prints the transformation between the fk_link_mast frame and a given target frame
# The default target frame is the link_grasp_center frame
# To change the target frame just pass it as an argument to the node, for ex. "target_frame:='fk_link_lift'"
class FrameListener(Node):

    def __init__(self):
        super().__init__('stretch_tf_listener')

        # Declare and acquire `target_frame` parameter
        self.declare_parameter('target_frame', 'link_grasp_center')
        self.target_frame = self.get_parameter(
            'target_frame').get_parameter_value().string_value

        # Start a Tf buffer that will store the tf information for a few seconds
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.tf_vector = [0,0,0]
        self.tf2_vec = [0,0,0]

        # Call on_timer function every second
        time_period = 3.0 # seconds
        self.timer = self.create_timer(time_period, self.on_timer)

    def on_timer(self):
        # Store frame names in variables that will be used to
        # compute transformations
        from_frame_rel = 'camera_color_frame'
        to_frame_rel = self.target_frame

        # Look up the transformation between target_frame and link_mast frames
        try:
            now = Time()
            trans = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                now)

            rev_trans = self.tf_buffer.lookup_transform(
                from_frame_rel,
                to_frame_rel,
                now)
        except TransformException as ex:
            self.get_logger().info(
                f'Could not transform {to_frame_rel} to {from_frame_rel}: {ex}')
            return

        tX = trans.transform.translation.x
        tY = trans.transform.translation.y
        tZ = trans.transform.translation.z

        self.tf_vector = [tX, tY, tZ]

        tX2 = rev_trans.transform.translation.x
        tY2 = rev_trans.transform.translation.y
        tZ2 = rev_trans.transform.translation.z
        
        self.tf2_vec = [tX2, tY2, tZ2]
        

        # self.get_logger().info(
                        # f'the pose of target frame {from_frame_rel} with reference to {to_frame_rel} is: {trans}')

        # self.get_logger().info(f'transform (x,y,z): {trans.transform.translation.x}, {trans.transform.translation.y}, {trans.transform.translation.z}')
        self.get_logger().info(f'Head to Grip: transform (x,y,z): {self.tf_vector}')
        self.get_logger().info(f'Grip to head: transform (x,y,z): {self.tf2_vec}')
        
        self.calculate_angles()



    def calculate_angles(self):
        dx = self.tf_vector[0]
        dy = self.tf_vector[1]
        dz = self.tf_vector[2]

        self.get_logger().info(f'Head to Grip: calculate angles (x,y,z): {dx}, {dy}, {dz}')
        
        # Calculate required pan and tilt angles geometrically
        import math
        target_pan = math.atan2(dy, dx)
        target_tilt = math.atan2(-dz, math.sqrt(dx**2 + dy**2))

        self.get_logger().info(f'Head to Grip: Cam Angles: Pan:{target_pan}  Tilt:{target_tilt}')


        dx2 = self.tf_vector[0]
        dy2 = self.tf_vector[1]
        dz2 = self.tf_vector[2]

        self.get_logger().info(f'Grip to head: calculate angles (x,y,z): {dx2}, {dy2}, {dz2}')
        
        # Calculate required pan and tilt angles geometrically
        import math
        target_pan2 = math.atan2(dy2, dx2)
        target_tilt2 = math.atan2(-dz2, math.sqrt(dx2**2 + dy2**2))

        self.get_logger().info(f'Grip to head: Cam Angles: Pan:{target_pan2}  Tilt:{target_tilt2}')




def main():
    rclpy.init()
    node = FrameListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()


if __name__ == '__main__':
    main()