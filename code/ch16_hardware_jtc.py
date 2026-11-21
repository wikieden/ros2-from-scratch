"""第 16 章代码对照：硬件组件的生命周期顺序、JTC 按时间插值、差速底盘把 cmd_vel 拆成左右轮速（纯 Python 模拟）。

讲义：ros2/notes/lessons/16-hardware-controllers.md
运行：uv run python ch16_hardware_jtc.py
为什么是模拟：硬件组件和控制器都是 C++ 插件。这里用 Python 写出同样的调用顺序；JTC 只做线性插值
（真 JTC 用样条，能接速度、加速度），差速公式见讲义附录"代码对照"一节的说明。
"""

import itertools


class FakeHardware:
    """一个 SystemInterface 的样子：生命周期回调里做的事按讲义第 1 步的表来，只有 ACTIVE 时 read / write 才干活。"""

    def __init__(self):
        self.state = "UNCONFIGURED"
        self.log: list[str] = []

    def on_init(self):
        self.log.append("on_init：读 URDF 里的参数，检查关节和接口（不和硬件通信）")

    def on_configure(self):
        self.log.append("on_configure：建立通信")
        self.state = "INACTIVE"

    def on_activate(self):
        self.log.append("on_activate：上电、松刹车")
        self.state = "ACTIVE"

    def read(self) -> bool:
        return self.state == "ACTIVE"

    def write(self) -> bool:
        return self.state == "ACTIVE"


def interpolate(waypoints: list[tuple[float, float]], t: float) -> float:
    """路点 (到达时刻, 关节位置)；两个路点之间按时间线性插值，过了最后一个就停在终点。"""
    if t <= waypoints[0][0]:
        return waypoints[0][1]
    for (t0, q0), (t1, q1) in itertools.pairwise(waypoints):
        if t0 <= t <= t1:
            return q0 + (q1 - q0) * (t - t0) / (t1 - t0)
    return waypoints[-1][1]


def diff_drive(v: float, w: float, wheel_separation: float, wheel_radius: float) -> tuple[float, float]:
    """cmd_vel（线速度 v、角速度 ω）→ 左右轮角速度：轮子线速度 = v ∓ ω·轮距/2，再除以轮半径。"""
    left = (v - w * wheel_separation / 2) / wheel_radius
    right = (v + w * wheel_separation / 2) / wheel_radius
    return left, right


def main() -> None:
    print("\n第一步 · 硬件组件：生命周期一步一步走，ACTIVE 之前 read / write 不干活")
    hw = FakeHardware()
    hw.on_init()
    print("  on_init 之后:", hw.state, "；read 干活吗？", hw.read())
    hw.on_configure()
    hw.on_activate()
    print("  activate 之后:", hw.state, "；read 干活吗？", hw.read())
    for line in hw.log:
        print("   ", line)

    print("\n第二步 · JTC：路点隔得远，控制器按时间插值，每拍算出当前该到的位置")
    waypoints = [(0.0, 0.0), (1.0, 1.0), (2.0, 0.5)]  # 三个路点是编的
    for t in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]:
        print(f"  t={t:.1f} s → joint1 = {interpolate(waypoints, t):.3f}")
    samples = [interpolate(waypoints, k / 1000) for k in range(2001)]
    print("  1 kHz 下 2 秒一共算了", len(samples), "个点")

    print("\n第二步（续）· 差速底盘：v=0.2 m/s、ω=1.0 rad/s，轮距 0.3 m、轮半径 0.05 m（编的）")
    left, right = diff_drive(0.2, 1.0, 0.3, 0.05)
    print(f"  左轮 {left:.1f} rad/s，右轮 {right:.1f} rad/s（往左转：右轮快）")


if __name__ == "__main__":
    main()
