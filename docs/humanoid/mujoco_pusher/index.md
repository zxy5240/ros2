# MuJoCo气动推杆推方块简单仿真

## 一、实验目的与环境说明
### 1.1 实验目的
1. 在MuJoCo里做一个简单的直线推杆机构
2. 写个脚本控制推杆反复把桌上的小方块推走
3. 熟悉一下MuJoCo里滑动关节和刚体碰撞的效果

### 1.2 实验环境
|项目|配置|
| ---- | ---- |
|操作系统|Ubuntu 20.04（VMware虚拟机）|
|ROS版本|ROS Noetic|
|MuJoCo版本|MuJoCo 2.1.1|
|编程语言|Python3|
|功能包|mujoco_pusher|

### 1.3 功能包目录结构
```
mujoco_pusher/
├── package.xml
├── CMakeLists.txt
├── launch/
│   └── pusher.launch
├── models/
│   └── pusher.xml      # 推杆和方块模型
└── scripts/
    └── main.py        # 主程序，控制推杆伸缩推方块
```

## 二、项目介绍
这个特别简单，就是一个工业上常见的直线推杆（气缸那种）：灰色底座上装着一根红色的圆杆，前面有个蓝色的推头，桌子上放了个绿色小方块。

程序控制推杆：伸出去把绿色方块推到桌子外面，然后缩回来，等一会再伸出去，循环往复。没有旋转关节来回摆，就是直线伸缩推东西，和之前那些关节摆动的项目完全不一样。

## 三、实现步骤
### 3.1 前置准备
确保MuJoCo和Python的mujoco库都装好了，`python3 -c "import mujoco"` 不报错就行。

### 3.2 建ROS功能包
```bash
cd ~/catkin_ws/src/humanoid
catkin_create_pkg mujoco_pusher rospy
cd ..
catkin_make
source devel/setup.bash
```

### 3.3 写模型文件
模型就三个部分：棕色桌子、灰色底座加红色推杆、绿色小方块。推杆是个滑动关节，只能沿着直线前后动，没有旋转。

### 3.4 写控制脚本
main.py逻辑特别简单：用时间控制，前2秒推杆伸出去，后2秒缩回来，4秒一个循环，推出去的时候蓝色推头就把绿色方块撞走。

## 四、运行方法
```bash
cd ~/catkin_ws/src/humanoid/mujoco_pusher/scripts
python3 main.py
```
弹出来MuJoCo窗口就能看到红色推杆一伸一缩，把绿色小方块推来推去。

用roslaunch启动也一样：
```bash
roslaunch mujoco_pusher pusher.launch
```

## 五、遇到的报错和解决办法
1. **报No module named 'mujoco'**
   老问题，`pip3 install mujoco` 装一下就行。

2. **方块直接穿过去了没被推动**
   就是摩擦系数设太小了，把模型里方块的摩擦改大一点就行，我调了好几次才推得动。

3. **推杆伸出去穿到桌子外面**
   把关节的行程范围调小一点，别伸太长就好了。

## 六、运行效果说明
跑起来之后：
- 红色推杆一开始缩在底座里
- 慢慢伸出去，蓝色推头碰到绿色方块，把方块往前推
- 方块被推到桌子边上掉下去
- 推杆再缩回来，循环

## 七、测试说明
我在Ubuntu20.04虚拟机上测的，模型加载正常，推杆能正常伸缩把方块推走，launch也能启动。

## 八、大模型声明
写代码框架和文档步骤的时候用DeepSeek辅助整理了一下。
