# -*- coding: utf-8 -*-
"""MuJoCo 环境封装：行车（龙门吊）吊挂负载。

只有两个自由度，没有轮子、没有接触 —— 这是刻意的：
前两个模块（差速车 + 高挂负载）都在"加速时车身俯仰掀翻"上卡住过，
去掉地面接触后这类问题从根上不存在。
"""

import math

import numpy as np

from . import config

import mujoco  # noqa: E402


class MujocoUnavailable(RuntimeError):
    pass


def wrap(a):
    return (a + math.pi) % (2.0 * math.pi) - math.pi


class State(object):
    """一帧状态。

    x        小车在导轨上的位置 (m)
    v        小车速度 (m/s)
    theta    摆角 (rad)，0 = 竖直下垂，正 = 向后摆
    theta_dot 摆角速度 (rad/s)
    """

    __slots__ = ("t", "x", "v", "theta", "theta_dot", "load_x", "load_z")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def __repr__(self):
        return ("t=%.2f x=%+.3f v=%+.3f θ=%+6.2f° θ̇=%+6.2f°/s"
                % (self.t, self.x, self.v, math.degrees(self.theta),
                   math.degrees(self.theta_dot)))


class CraneEnv(object):

    def __init__(self, scene_path, verbose=True):
        try:
            self.model = mujoco.MjModel.from_xml_path(scene_path)
        except Exception as exc:
            raise MujocoUnavailable("无法加载场景 %s：%s" % (scene_path, exc))
        self.data = mujoco.MjData(self.model)
        self.dt = float(self.model.opt.timestep)
        self.steps_per_control = max(1, int(round(1.0 / (self.dt * config.CONTROL_HZ))))

        self._cart_q = self._qposadr("slide_joint")
        self._cart_v = self._dofadr("slide_joint")
        self._sw_q = self._qposadr("swing_joint")
        self._sw_v = self._dofadr("swing_joint")
        self._tip = self._id(mujoco.mjtObj.mjOBJ_SITE, "tip")
        self._renderer = None

        self.reset()
        if verbose:
            print("[MuJoCo] %s（nq=%d, nu=%d, dt=%.4f, 总质量 %.1f kg）"
                  % (scene_path, self.model.nq, self.model.nu, self.dt,
                     float(self.model.body_mass.sum())))

    # ------------------------------------------------------------------
    def _id(self, objtype, name):
        i = mujoco.mj_name2id(self.model, objtype, name)
        if i < 0:
            raise MujocoUnavailable("场景里找不到 %s" % name)
        return i

    def _dofadr(self, joint):
        return int(self.model.jnt_dofadr[self._id(mujoco.mjtObj.mjOBJ_JOINT, joint)])

    def _qposadr(self, joint):
        return int(self.model.jnt_qposadr[self._id(mujoco.mjtObj.mjOBJ_JOINT, joint)])

    # ------------------------------------------------------------------
    def reset(self, x=0.0, theta=0.0):
        d = self.data
        mujoco.mj_resetData(self.model, d)
        d.qpos[self._cart_q] = float(x)
        d.qpos[self._sw_q] = float(theta)
        d.qvel[:] = 0.0
        d.ctrl[:] = 0.0
        mujoco.mj_forward(self.model, d)
        return self.state()

    def set_force(self, f):
        """给小车施加沿导轨的驱动力 (N)。"""
        lim = float(self.model.actuator_ctrlrange[0][1])
        self.data.ctrl[0] = max(-lim, min(lim, float(f)))

    def step(self, n_control=1):
        for _ in range(int(n_control)):
            for _k in range(self.steps_per_control):
                mujoco.mj_step(self.model, self.data)
        return self.state()

    # ------------------------------------------------------------------
    def state(self):
        d = self.data
        return State(t=float(d.time),
                     x=float(d.qpos[self._cart_q]),
                     v=float(d.qvel[self._cart_v]),
                     theta=float(d.qpos[self._sw_q]),
                     theta_dot=float(d.qvel[self._sw_v]),
                     load_x=float(d.site_xpos[self._tip][0]),
                     load_z=float(d.site_xpos[self._tip][2]))

    def sway_deg(self):
        return abs(math.degrees(self.state().theta))

    # ------------------------------------------------------------------
    def render(self, width=480, height=270, camera="chase"):
        """渲染一帧；后端按 default → osmesa → egl 逐个尝试。"""
        import os
        if self._renderer is not None:
            self._renderer.update_scene(self.data, camera=camera)
            return self._renderer.render()
        cands = [os.environ.get("MUJOCO_GL") or "default"]
        if not os.environ.get("DISPLAY"):
            cands += ["osmesa", "egl"]
        last = None
        for backend in cands:
            os.environ["MUJOCO_GL"] = backend
            try:
                self._renderer = mujoco.Renderer(self.model, height, width)
                break
            except Exception as exc:      # noqa: BLE001
                last = exc
                self._renderer = None
        if self._renderer is None:
            raise RuntimeError("没有可用的渲染后端（试过 %s）：%s" % (cands, last))
        self._renderer.update_scene(self.data, camera=camera)
        return self._renderer.render()

    def close(self):
        if self._renderer is not None:
            try:
                self._renderer.close()
            except Exception:
                pass
            self._renderer = None


def describe_env():
    import os
    import platform
    return " | ".join(["python %s" % platform.python_version(),
                       "numpy %s" % np.__version__,
                       "mujoco %s" % mujoco.__version__,
                       "MUJOCO_GL=%s" % (os.environ.get("MUJOCO_GL") or "未设置")])
