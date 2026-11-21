"""第 15 章代码对照：ros2_control 的一个周期 read() → update() → write()，接口就是共享变量（纯 Python 模拟）。

讲义：ros2/notes/lessons/15-realtime-ros2-control.md
运行：uv run python ch15_control_loop.py
为什么是模拟：ros2_control 是 C++ 框架，本机也没有 ROS 2。这里用字典当"接口"，用 mock 硬件（命令原样回写成状态，
讲义第 3 步末尾）跑几个周期；最后量一下普通 Python 循环每 1 ms 一拍的实际抖动，看为什么快回路不放 Python。
"""

import itertools
import statistics
import time


class MockSystem:
    """mock_components/GenericSystem 的样子：write 时把命令记下，下一次 read 时原样当成状态报上来。"""

    def __init__(self, joints: list[str]):
        self.state = {f"{j}/position": 0.0 for j in joints}  # 状态接口：硬件报上来的，只读
        self.command = {f"{j}/position": 0.0 for j in joints}  # 命令接口：发给硬件的
        self._hw = dict(self.state)  # "硬件"里真实的位置

    def read(self):
        self.state.update(self._hw)

    def write(self):
        self._hw.update(self.command)


class StepTowardController:
    """一个简单的位置控制器：每拍朝目标走最多 max_step（编的控制律，只为看清 read / update / write 的分工）。"""

    def __init__(self, joint: str, target: float, max_step: float):
        self.joint, self.target, self.max_step = joint, target, max_step

    def command_interfaces(self) -> list[str]:
        return [f"{self.joint}/position"]

    def update(self, state: dict, command: dict):
        now = state[f"{self.joint}/position"]
        err = self.target - now
        command[f"{self.joint}/position"] = now + max(-self.max_step, min(self.max_step, err))


def control_loop(hw: MockSystem, controller: StepTowardController, cycles: int) -> list[float]:
    """controller manager 的回路：每个周期 read → update → write。返回每拍读到的关节位置。"""
    trace = []
    for _ in range(cycles):
        hw.read()  # RM：硬件 → 状态接口
        trace.append(round(hw.state[f"{controller.joint}/position"], 3))
        controller.update(hw.state, hw.command)  # CM：控制器读状态、写命令
        hw.write()  # RM：命令接口 → 硬件
    return trace


def measure_python_jitter(period_s: float = 0.001, n: int = 200) -> dict:
    """普通 Python：sleep 1 ms 一拍，量实际每拍隔多久。每台电脑、每次结果都不一样。"""
    stamps = []
    for _ in range(n):
        stamps.append(time.perf_counter())
        time.sleep(period_s)
    gaps = [(b - a) * 1000 for a, b in itertools.pairwise(stamps)]
    return {"平均 ms": round(statistics.mean(gaps), 3), "最长 ms": round(max(gaps), 3),
            "最大抖动 ms": round(max(abs(g - period_s * 1000) for g in gaps), 3)}


def main() -> None:
    print("\n第二步 · 一个周期：read → update → write；mock 硬件把命令原样当成下一拍的状态")
    hw = MockSystem(["joint1", "joint2"])
    ctrl = StepTowardController("joint1", target=0.05, max_step=0.01)
    print("  控制器要独占的命令接口:", ctrl.command_interfaces())
    print("  前 8 拍读到的 joint1/position:", control_loop(hw, ctrl, 8))

    print("\n第二步（续）· 接口就是共享变量：读写只是一次赋值")
    print("  状态接口:", hw.state)
    print("  命令接口:", hw.command)

    print("\n第一步 · 实时要的是准时：量一下普通 Python 每 1 ms 一拍的抖动（每次结果不同）")
    print("  ", measure_python_jitter())


if __name__ == "__main__":
    main()
