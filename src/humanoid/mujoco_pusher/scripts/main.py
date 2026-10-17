#!/usr/bin/env python3
import mujoco
import mujoco.viewer
import time

model = mujoco.MjModel.from_xml_path("../models/pusher.xml")
data = mujoco.MjData(model)

with mujoco.viewer.launch_passive(model, data) as viewer:
    start_time = time.time()
    while viewer.is_running():
        t = time.time() - start_time
        # 周期循环：0-2秒推杆伸出去推方块，2-4秒缩回来
        if t < 2:
            data.ctrl[0] = 0.55  # 推杆伸出去
        else:
            data.ctrl[0] = 0.0   # 推杆缩回来
        
        # 4秒一个周期
        if t > 4:
            start_time = time.time()
        
        mujoco.mj_step(model, data)
        viewer.sync()
