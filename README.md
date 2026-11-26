# Isaac ROS with Isaac Sim on a Clearpath Dingo

Launch files, RViz layouts and scripts for the Isaac ROS tutorial series on [SPARC Lab](https://www.youtube.com/@SPARCLab07).
Isaac Sim 6.1 + Isaac ROS 3.2 (ROS 2 Humble).

## Output

**cuVSLAM: visual odometry and sparse 3D map**

![cuVSLAM output](images/cuvslam.png)

**nvblox: 3D mesh and 2D occupancy grid**

![nvblox output](images/nvblox.png)

## Contents

| Path | What it is |
|---|---|
| `launch/sim_cuvslam.launch.py` | cuVSLAM (stereo) + RViz |
| `launch/sim_nvblox.launch.py` | cuVSLAM + nvblox + RViz |
| `rviz/` | saved RViz layouts |
| `docker/Dockerfile.isaac_ros` | extra packages for the Isaac ROS dev container |
| `joystick_teleop.py` | drive the robot with a joystick (`/cmd_vel`) |
| `Dingo.usd` | Isaac Sim scene |
