# Isaac ROS with Isaac Sim on a Clearpath Dingo

Launch files, RViz layouts and scripts for the Isaac ROS tutorial series on [SPARC Lab](https://www.youtube.com/@SPARCLab07).
Isaac Sim 6.1 + Isaac ROS 3.2 (ROS 2 Humble).

## Setup

```
# clone this repo as your Isaac ROS workspace
git clone https://github.com/sahilrajpurkar03/isaac_ros-dev.git ~/isaac_ros-dev
export ISAAC_ROS_WS=~/isaac_ros-dev

# src/ is not in this repo, clone NVIDIA's isaac_ros_common into it (Isaac ROS 3.2)
mkdir -p ${ISAAC_ROS_WS}/src && cd ${ISAAC_ROS_WS}/src
git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git
```

Then follow the tutorials on the [SPARC Lab YouTube channel](https://www.youtube.com/@SPARCLab07).

## Output

**cuVSLAM: visual odometry and sparse 3D map**

![cuVSLAM output](output/cuvslam.gif)

**nvblox: 3D mesh and 2D occupancy grid**

![nvblox output](output/nvblox.gif)

## Contents

| Path | What it is |
|---|---|
| `launch/sim_cuvslam.launch.py` | cuVSLAM (stereo) + RViz |
| `launch/sim_nvblox.launch.py` | cuVSLAM + nvblox + RViz |
| `rviz/` | saved RViz layouts |
| `docker/Dockerfile.isaac_ros` | extra packages for the Isaac ROS dev container |
| `joystick_teleop.py` | drive the robot with a joystick (`/cmd_vel`) |
| `Dingo.usd` | Isaac Sim scene |
