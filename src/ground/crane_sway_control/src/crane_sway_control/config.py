# -*- coding: utf-8 -*-
"""集中配置：路径、几何、控制增益。"""

import os
from pathlib import Path

# config.py 在 <包>/src/crane_sway_control/ 下，往上是三层才是包根
PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SCENE = PACKAGE_ROOT / "models" / "crane_sway.xml"
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "results"


def resolve_scene_path(scene=None):
    p = Path(scene) if scene else DEFAULT_SCENE
    p = p.expanduser()
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return str(p)


# ---------------------------------------------------------------------------
CONTROL_HZ = 50.0

# 几何（与 models/crane_sway.xml 对应）
ROD_LENGTH = 0.60          # 吊杆长，单摆周期 2π√(l/g) ≈ 1.55 s
CART_MASS = 8.0
LOAD_MASS = 5.0
RAIL_LIMIT = 1.40          # 导轨行程 ±1.4 m

# 控制：小车定位 PD + 防摇反馈
KP_POS = 8.0              # 位置误差 → 加速度
KD_VEL = 8.0               # 速度阻尼
K_SWAY = 20.0              # 摆角 → 加速度（防摇主力）
KD_SWAY = 9.0              # 摆角速度 → 加速度
A_MAX = 2.0                # 加速度限幅 (m/s²)

# 判定"晃完了"的阈值
SWAY_SETTLED_DEG = 1.0
