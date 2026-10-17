#!/usr/bin/env python3
import rospy
import mujoco
import mujoco.viewer
import numpy as np
from std_msgs.msg import Float64MultiArray

# 加载模型
model = mujoco.MjModel.from_xml_path("../models/two_dof_arm.xml")
data = mujoco.MjData(model)

# 当前目标角度，初始都是0
target_angles = [0.0, 0.0]

def callback(msg):
    global target_angles
    # 收到话题消息就更新目标角度
    if len(msg.data) >= 2:
        target_angles[0] = msg.data[0]
        target_angles[1] = msg.data[1]
        rospy.loginfo(f"收到新指令: 肩膀角度={target_angles[0]:.2f}, 手肘角度={target_angles[1]:.2f}")

if __name__ == "__main__":
    rospy.init_node("mujoco_ros_arm")
    rospy.Subscriber("/arm_goal", Float64MultiArray, callback, queue_size=1)
    rospy.loginfo("机械臂节点启动了，发角度指令到 /arm_goal 就能控制它动")
    
    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running() and not rospy.is_shutdown():
            # 平滑转到目标角度
            data.ctrl[0] += (target_angles[0] - data.ctrl[0]) * 0.1
            data.ctrl[1] += (target_angles[1] - data.ctrl[1]) * 0.1
            
            mujoco.mj_step(model, data)
            viewer.sync()
            rospy.sleep(0.01)
