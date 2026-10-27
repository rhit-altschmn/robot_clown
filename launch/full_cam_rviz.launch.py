import os
from ament_index_python.packages import get_package_share_directory, get_package_share_path
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PythonExpression, TextSubstitution
from launch.conditions import IfCondition, LaunchConfigurationEquals
from launch_ros.actions import Node

configurable_parameters = [
                        # {'name': 'resolution',                          'default': 'high', 'description': 'resolution of the color/depth images low or high'},
                        #    {'name': 'publish_frustum_viz',                 'default': 'false', 'description': 'whether to pub viz of camera frustums'},
                           {'name': 'publish_upright_img',                 'default': 'true', 'description': 'whether to pub rotated upright color image'},
                          ]

def declare_configurable_parameters(parameters):
    return [DeclareLaunchArgument(param['name'], default_value=param['default'], description=param['description']) for param in parameters]

def generate_launch_description():
    #  publish_frustum_viz = LaunchConfiguration('publish_frustum_viz')
    publish_upright_img = LaunchConfiguration('publish_upright_img')
    #  resolution = LaunchConfiguration('resolution')

    robot_clown_path = get_package_share_path('robot_clown')


    # d435i_basic_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('stretch_core'), 'launch'),
    #         '/d435i_basic.launch.py'])
    #     )

    # d405_basic_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource([os.path.join(
    #         get_package_share_directory('stretch_core'), 'launch'),
    #         '/d405_basic.launch.py'])
    #     )
    
    # upright_rotater = Node(
        # condition=IfCondition(
        #     PythonExpression([
        #     publish_upright_img
        #     ])),
        # package='image_rotate',
        # executable='upright_rotater',
        # remappings=[
        #     ('image', '/camera/color/image_raw'),
        #     ('rotated/image', '/camera/color/upright_image_raw'),
        # ],
        # parameters=[
        #     {'target_frame_id': "", 
        #     'target_x': '-1.5708'}
        #     ],
        # )

    tf_show = Node(
        package='stretch_ros_tutorials',
        executable='tf_broadcaster',
        output='screen'
    )

    tf_read = Node(
        package='robot_clown',
        executable='stretch_tf_listener',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', str(robot_clown_path / 'rviz' / 'good_views.rviz')]
    )
        

    return LaunchDescription(declare_configurable_parameters(configurable_parameters) + [
        # d435i_basic_launch,
        # d405_basic_launch,
        # upright_rotater,
        tf_show,
        tf_read,
        rviz_node,
        ])
