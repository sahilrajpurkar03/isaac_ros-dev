# cuVSLAM stereo on the Isaac Sim cameras (Isaac ROS 3.2, ROS 2 Humble).
# Lines marked CHANGE are the ones to edit for your own robot, camera topics and frame names.
# Check the parameter names of your version with: ros2 param list /visual_slam_node
import os

import launch
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'use_sim_time': True,
            'num_cameras': 2,
            'rectified_images': True,
            'enable_imu_fusion': False,
            # wheeled robot on a flat floor: keep cuVSLAM on the ground plane (added after z drifted 0.29 m in the first loop test)
            'enable_ground_constraint_in_odometry': True,
            'enable_ground_constraint_in_slam': True,
            'base_frame': 'base_link',   # CHANGE: your robot base frame
            'odom_frame': 'odom',        # CHANGE: your odometry frame
            'map_frame': 'map',
            'camera_optical_frames': ['left_camera', 'right_camera'],   # CHANGE: the frame_id of your left and right camera images
            # first test: do NOT publish transforms (Isaac Sim already publishes odom > base_link)
            'publish_odom_to_base_tf': False,
            'publish_map_to_odom_tf': False,
            # RViz views of the map
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,
            # TUNE: how many poses the path in RViz keeps; older poses are dropped, so a small value makes the path vanish behind the robot
            'path_max_size': 3000,
        }],
        # CHANGE: the right-hand side of each line is YOUR topic name (ros2 topic list)
        remappings=[
            ('visual_slam/image_0', '/left/rgb'),
            ('visual_slam/camera_info_0', '/left/camera_info'),
            ('visual_slam/image_1', '/right/rgb'),
            ('visual_slam/camera_info_1', '/right/camera_info'),
        ])

    container = ComposableNodeContainer(
        name='visual_slam_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_mt',
        composable_node_descriptions=[visual_slam_node],
        output='screen')

    # RViz with our saved layout (sim_cuvslam.rviz must be in the rviz folder next to the launch folder: <workspace>/rviz/)
    rviz_config = os.path.normpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'rviz', 'sim_cuvslam.rviz'))
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen')

    return launch.LaunchDescription([container, rviz])
