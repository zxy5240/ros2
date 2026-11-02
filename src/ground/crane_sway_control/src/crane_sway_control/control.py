# -*- coding: utf-8 -*-
"""防摇控制：小车定位 PD + 摆角反馈。

控制律
    a = kp·(x_target − x) − kd·v − k_sway·θ − kd_sway·θ̇
    F = (m_cart + m_load) · a

为什么摆角项是**负号**：
    小车往右加速时，吊着的负载因为惯性会"滞后"，摆角 θ 与加速度方向相反。
    再加一个与 θ 反向的加速度，等于让小车"追"着摆球走，把摆幅压下去。
    这就是行车防摇最常见的做法（输入整形的连续化版本）。

为什么不用 LQR：本模块没有解 Riccati 方程，增益是网格搜索选出来的
（k_sway 从 8 试到 20，摆角峰值从 16.6° 降到 11.9°）。称它为 PD 是准确的。
"""

from . import config


class SwayController(object):

    def __init__(self, kp=None, kd=None, k_sway=None, kd_sway=None, sway=True):
        self.kp = config.KP_POS if kp is None else kp
        self.kd = config.KD_VEL if kd is None else kd
        self.k_sway = config.K_SWAY if k_sway is None else k_sway
        self.kd_sway = config.KD_SWAY if kd_sway is None else kd_sway
        self.sway = sway

    def accel(self, st, x_target):
        a = self.kp * (x_target - st.x) - self.kd * st.v
        if self.sway:
            a -= self.k_sway * st.theta + self.kd_sway * st.theta_dot
        return max(-config.A_MAX, min(config.A_MAX, a))

    def force(self, st, x_target):
        return (config.CART_MASS + config.LOAD_MASS) * self.accel(st, x_target)

    def gains(self):
        return dict(kp=self.kp, kd=self.kd, k_sway=self.k_sway,
                    kd_sway=self.kd_sway, sway=self.sway)
