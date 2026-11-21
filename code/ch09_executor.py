"""第 9 章代码对照：慢回调怎么挤掉控制回路，回调组 + 多线程怎么救回来（纯 Python 按毫秒模拟时间线）。

讲义：ros2/notes/lessons/09-executors.md
运行：uv run python ch09_executor.py
为什么是模拟：本机没有 rclpy；而且真 Python 线程受 GIL 和系统调度影响，每次跑结果都不一样。
这里把时间切成 1 毫秒一格，按讲义第 3 步的例子（50 Hz 控制定时器、30 Hz 图像订阅、图像回调 40 ms）
一格一格推进，结果每次都一样。规则：定时器晚了不补发，到点时上一拍还没跑就算漏拍；图像只留最新一张（Keep last 1）。
"""

from dataclasses import dataclass


@dataclass
class Callback:
    name: str
    period_ms: float  # 多久来一次
    cost_ms: int  # 跑一次要多久
    group: str  # 属于哪个互斥回调组
    is_timer: bool = False  # 定时器排在订阅前面先看


def simulate(callbacks: list[Callback], threads: int, total_ms: int = 1000) -> dict:
    """返回每个回调：跑了几次、漏了几拍、最多晚了多少毫秒才开始。"""
    pending: dict[str, float | None] = {c.name: None for c in callbacks}  # 等着跑的那一次是几点到的
    next_release = {c.name: c.period_ms for c in callbacks}
    stats = {c.name: {"runs": 0, "missed": 0, "max_late_ms": 0.0} for c in callbacks}
    busy: list[tuple[int, str]] = []  # (忙到几点, 占着哪个组)
    for t in range(total_ms):
        busy = [(end, g) for end, g in busy if end > t]
        for c in callbacks:
            while next_release[c.name] <= t:
                if c.is_timer and pending[c.name] is not None:
                    stats[c.name]["missed"] += 1  # 上一拍还没跑，这一拍又到了：漏拍（定时器晚了不补发）
                pending[c.name] = next_release[c.name]  # 定时器记最新一拍；图像只留最新一张
                next_release[c.name] += c.period_ms
        for c in sorted(callbacks, key=lambda c: not c.is_timer):  # 定时器排在前面，先看
            if len(busy) >= threads:
                break
            if pending[c.name] is None or any(g == c.group for _, g in busy):
                continue
            late = t - pending[c.name]
            s = stats[c.name]
            s["runs"] += 1
            s["max_late_ms"] = max(s["max_late_ms"], round(late, 1))
            pending[c.name] = None
            busy.append((t + c.cost_ms, c.group))
    return stats


def main() -> None:
    print("\n第一步 · 单线程 executor：一个线程、默认组（互斥），图像回调一跑 40 ms，控制回路只能等")
    single = [Callback("control 50 Hz", 20, 1, "default", True), Callback("image 30 Hz", 1000 / 30, 40, "default")]
    for name, s in simulate(single, threads=1).items():
        print(f"  {name:<14} 跑了 {s['runs']:>2} 次  漏拍 {s['missed']:>2}  最多晚 {s['max_late_ms']} ms")

    print("\n第二步 · 多线程 executor + 两个互斥组：控制一组、图像一组，两个线程")
    grouped = [Callback("control 50 Hz", 20, 1, "control_group", True),
               Callback("image 30 Hz", 1000 / 30, 40, "io_group")]
    for name, s in simulate(grouped, threads=2).items():
        print(f"  {name:<14} 跑了 {s['runs']:>2} 次  漏拍 {s['missed']:>2}  最多晚 {s['max_late_ms']} ms")


if __name__ == "__main__":
    main()
