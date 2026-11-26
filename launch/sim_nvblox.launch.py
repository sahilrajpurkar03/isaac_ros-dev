# nvblox on the Isaac Sim depth camera, with cuVSLAM as the pose source (Isaac ROS 3.2, ROS 2 Humble).
# Lines marked CHANGE are the ones to edit for your own robot, camera topics and frame names.
# Lines marked TUNE depend on the robot size and the camera mounting.
import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


def generate_launch_description():
    # NVIDIA's default nvblox parameters (installed with the package); our own settings are added below
    nvblox_base = os.path.join(
        get_package_share_directory('nvblox_examples_bringup'), 'config', 'nvblox', 'nvblox_base.yaml')

    # cuVSLAM: visual odometry only (as in NVIDIA's nvblox examples), publishes odom > base_link
    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'use_sim_time': True,
            'num_cameras': 2,
            'rectified_images': True,
            'enable_imu_fusion': False,
            'enable_localization_n_mapping': False,
            'enable_ground_constraint_in_odometry': True,
            'base_frame': 'base_link',   # CHANGE: your robot base frame
            'odom_frame': 'odom',        # CHANGE: your odometry frame
            'map_frame': 'map',
            'camera_optical_frames': ['left_camera', 'right_camera'],   # CHANGE: the frame_id of your left and right camera images
            # cuVSLAM is now the source of odom > base_link (switch the simulator's own odom > base_link publisher off)
            'publish_odom_to_base_tf': True,
            'publish_map_to_odom_tf': False,
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

    nvblox_node = ComposableNode(
        name='nvblox_node',
        package='nvblox_ros',
        plugin='nvblox::NvbloxNode',
        parameters=[
            nvblox_base,
            {
                'use_sim_time': True,
                'num_cameras': 1,
                'use_lidar': False,
                'input_qos': 'DEFAULT',   # NVIDIA's Isaac Sim setting: reliable delivery from Isaac Sim
                # TUNE: NVIDIA's default (7.0) deletes the map farther than 7 m from the robot; -1.0 keeps the whole map (uses more GPU memory)
                'map_clearing_radius_m': -1.0,
                # TUNE: rates must be set at startup, they are ignored when changed at runtime. 0.0 switches the job off.
                'clear_map_outside_radius_rate_hz': 0.0,   # no clearing of far-away blocks
                'decay_tsdf_rate_hz': 0.0,                 # default 5.0 would decay and delete parts of the map you are not looking at
                # TUNE: NVIDIA's defaults hide voxels beyond 7 m (and above 2 m) from the robot in the visualization
                'layer_visualization_exclusion_radius_m': 100.0,
                'layer_visualization_exclusion_height_m': 100.0,
                # TUNE: height band (in meters, relative to the global frame) that becomes the 2D costmap slice
                'static_mapper.esdf_slice_height': 0.1,
                'static_mapper.esdf_slice_min_height': 0.05,
                'static_mapper.esdf_slice_max_height': 0.4,
            },
        ],
        # CHANGE: the right-hand side of each line is YOUR depth and color topic (ros2 topic list)
        remappings=[
            ('camera_0/depth/image', '/left/depth'),
            ('camera_0/depth/camera_info', '/left/camera_info'),
            ('camera_0/color/image', '/left/rgb'),
            ('camera_0/color/camera_info', '/left/camera_info'),
        ])

    container = ComposableNodeContainer(
        name='nvblox_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container_isolated',
        composable_node_descriptions=[visual_slam_node, nvblox_node],
        output='screen')

    # RViz with our saved layout if sim_nvblox.rviz is in the rviz folder next to the launch folder (<workspace>/rviz/), otherwise plain RViz
    rviz_config = os.path.normpath(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'rviz', 'sim_nvblox.rviz'))
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config] if os.path.exists(rviz_config) else [],
        parameters=[{'use_sim_time': True}],
        # The nvblox mesh display crashes RViz without this (RViz no longer ships the shader it asks for)
        additional_env={'ISAAC_ROS_NVBLOX_PLUGIN_FORCE_FALLBACK_MATERIAL': '1'},
        output='screen')

    return launch.LaunchDescription([container, rviz])
