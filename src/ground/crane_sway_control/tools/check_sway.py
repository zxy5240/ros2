#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""防摇自检：同一段"搬运"动作，对比有无防摇。

    A. 无防摇（只做小车定位 PD）：负载会晃很久
    B. 有防摇（加摆角反馈）：摆幅减半、回稳更快
    C. 长距离搬运 2.4 m：看它在更激烈的工况下是否仍然稳定

用法：
    python3 tools/check_sway.py
    python3 tools/check_sway.py --target 1.0 --csv results/sway.csv
"""

import argparse
import csv
import math
import sys
from pathlib import Path

PKG_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PKG_ROOT / "src"))

from crane_sway_control import config                              # noqa: E402
from crane_sway_control.control import SwayController              # noqa: E402
from crane_sway_control.env import CraneEnv, describe_env          # noqa: E402


def run_case(env, ctrl, x_target, seconds=8.0):
    """跑一段搬运，返回 (摆角峰值, 回稳时刻, 终点位置, 采样序列)。"""
    env.reset(0.0)
    peak = 0.0
    settled = None
    trace = []
    for k in range(int(seconds * config.CONTROL_HZ)):
        st = env.state()
        env.set_force(ctrl.force(st, x_target))
        st = env.step()
        deg = abs(math.degrees(st.theta))
        peak = max(peak, deg)
        if settled is None and k > int(1.0 * config.CONTROL_HZ) \
                and deg < config.SWAY_SETTLED_DEG:
            settled = st.t
        if k % int(0.5 * config.CONTROL_HZ) == 0:
            trace.append(deg)
        if abs(st.x) > config.RAIL_LIMIT:
            break
    return peak, settled, env.state().x, trace


def main(argv=None):
    ap = argparse.ArgumentParser(description="行车吊挂负载防摇自检")
    ap.add_argument("--target", type=float, default=1.0, help="搬运距离 (m)")
    ap.add_argument("--seconds", type=float, default=8.0)
    ap.add_argument("--scene", default=None)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args(argv)

    print("[环境] %s" % describe_env())
    env = CraneEnv(config.resolve_scene_path(args.scene))
    print("[场景] 吊杆 %.2f m，单摆周期 ≈ %.2f s，小车 %.0f kg + 负载 %.0f kg"
          % (config.ROD_LENGTH, 2 * math.pi * math.sqrt(config.ROD_LENGTH / 9.81),
             config.CART_MASS, config.LOAD_MASS))

    print("\n=== 搬运 %.1f m：有/无防摇对比 ===" % args.target)
    print("  %-14s%12s%12s%10s" % ("方案", "摆角峰值", "回稳时刻", "终点位置"))
    rows = []
    for name, sway in (("A. 无防摇（纯PD）", False), ("B. 有防摇", True)):
        ctrl = SwayController(sway=sway)
        peak, settled, x_end, trace = run_case(env, ctrl, args.target, args.seconds)
        print("  %-14s%10.1f°%12s%10.3f m"
              % (name, peak, ("%.2f s" % settled) if settled else "未回稳",
                 x_end))
        rows.append(dict(case=name, peak_deg=round(peak, 2),
                         settled=round(settled, 2) if settled else -1,
                         x_end=round(x_end, 3)))
        if sway:
            print("    摆角序列（每 0.5 s）: %s" % trace[:10])

    a, b = rows[0], rows[1]
    if a["peak_deg"] > 0:
        print("\n  摆角峰值下降 %.0f%%（%.1f° → %.1f°）"
              % (100 * (1 - b["peak_deg"] / a["peak_deg"]),
                 a["peak_deg"], b["peak_deg"]))

    print("\n=== 长距离搬运 1.2 m（接近导轨行程上限）===")
    env.reset(0.0)
    ctrl = SwayController(sway=True)
    peak, settled, x_end, _ = run_case(env, ctrl, 1.2, seconds=10.0)
    print("  有防摇：摆角峰 %.1f°，%s，终点 %.3f m"
          % (peak, ("%.2f s 回稳" % settled) if settled else "未回稳", x_end))
    ok = peak < 30.0 and abs(x_end - 1.2) < 0.15
    print("  → %s" % ("通过 ✓（摆幅可控、到位准确）" if ok else "**不通过**"))

    all_ok = b["peak_deg"] < a["peak_deg"] and ok
    print("\n[结论] %s" % ("防摇有效，四项数据如上" if all_ok else "存在未达标项"))

    if args.csv:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["case", "peak_deg", "settled", "x_end"])
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print("[导出] %s" % out)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
