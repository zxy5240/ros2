# MuJoCo机械臂ROS话题控制简单仿真

## 一、实验目的与环境说明
### 1.1 实验目的
1. 把之前写的MuJoCo机械臂改成真正的ROS节点
2. 学会用ROS话题从外部发指令控制机器人动作
3. 熟悉一下ROS订阅/发布通信的基本流程

### 1.2 实验环境
|项目|配置|
| ---- | ---- |
|操作系统|Ubuntu 20.04（VMware虚拟机）|
|ROS版本|ROS Noetic|
|MuJoCo版本|MuJoCo 2.1.1|
|编程语言|Python3|
|功能包|mujoco_ros_arm|

### 1.3 功能包目录结构
```
mujoco_ros_arm/
├── package.xml
├── CMakeLists.txt
├── launch/
│   └── arm_ros.launch
├── models/
│   └── two_dof_arm.xml      # 两自由度机械臂模型
└── scripts/
    └── main.py        # ROS节点，订阅话题控制机械臂
```

## 二、项目介绍
之前写的MuJoCo机械臂都是打开之后就自己来回摆，控制角度全写死在代码里。这次改了一下，让它变成一个正常的ROS节点：启动之后不自己动，等着外部发话题指令，你发什么角度它就转到什么角度，和真实机器人的控制方式一样。

简单说就是机械臂在MuJoCo里跑仿真，但是通过ROS话题和外界通信，你可以新开终端发指令，也可以写别的节点控制它，很灵活。

## 三、实现步骤
### 3.1 前置准备
确保MuJoCo和ROS Noetic都装好了，`python3 -c "import mujoco"` 不报错就行。

### 3.2 建ROS功能包
```bash
cd ~/catkin_ws/src/humanoid
catkin_create_pkg mujoco_ros_arm rospy std_msgs
cd ..
catkin_make
source devel/setup.bash
```

### 3.3 机械臂模型
模型还是简单的两关节：蓝色大臂、橙色小臂、末端红色小球，和之前那个差不多，就是这次不写自动摆动的逻辑了。

### 3.4 写ROS节点脚本
main.py里核心就是两个部分：
1. 初始化一个订阅者，监听 `/arm_goal` 话题
2. 收到消息就把目标角度记下来，机械臂平滑转过去

```python
def callback(msg):
    global target_angles
    target_angles[0] = msg.data[0]
    target_angles[1] = msg.data[1]
```

## 四、运行方法
先开roscore：
```bash
roscore
```
新开终端启动机械臂节点：
```bash
cd ~/catkin_ws/src/humanoid/mujoco_ros_arm/scripts
python3 main.py
```
正常会弹出MuJoCo窗口，机械臂初始是直立不动的。

这时候再新开个终端，发个角度指令，比如让肩膀转0.5弧度、手肘转0.8弧度：
```bash
rostopic pub /arm_goal std_msgs/Float64MultiArray "data: [0.5, 0.8]"
```
发完就能看到机械臂慢慢转到那个位置停下来。

想转别的角度就改后面两个数字就行，范围大概在-1.5到1.5之间，别太大就不会乱撞。

用roslaunch一键启动也可以：
```bash
roslaunch mujoco_ros_arm arm_ros.launch
```

## 五、遇到的报错和解决办法
1. **报ModuleNotFoundError: No module named 'mujoco'**
   老问题，`pip3 install mujoco` 装一下就行。

2. **发话题没反应**
   检查话题名是不是写对了，是 `/arm_goal`，别拼错，用 `rostopic list` 看一下节点在不在。

3. **机械臂动太快晃来晃去**
   把main.py里平滑系数0.1改小一点，比如改成0.05，就转得更稳了。

## 六、运行效果说明
跑起来之后：
- 初始状态机械臂直立不动
- 发完指令机械臂平滑转到指定角度
- 终端会打印收到的目标角度
- 你可以连续发不同角度的指令，它就跟着转

## 七、测试说明
我在Ubuntu20.04虚拟机上测的，节点启动正常，发话题能控制机械臂转角度，launch也能正常启动。

## 八、大模型声明
写代码框架和文档步骤的时候用DeepSeek辅助整理了一下。
