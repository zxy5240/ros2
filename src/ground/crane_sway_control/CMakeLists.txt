cmake_minimum_required(VERSION 3.0.2)
project(crane_sway_control)

find_package(catkin REQUIRED COMPONENTS rospy std_msgs geometry_msgs)

catkin_python_setup()
catkin_package()

# 节点脚本还没写（下一步），先留空：catkin_install_python 指向不存在的文件
# 会让 catkin_make 直接失败，所以等 scripts/ 建好后再打开这一段。

install(DIRECTORY launch config models
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
