"""第 20 章代码对照：近似时间同步、动作块缓冲区按时刻取一步、时间集成衔接、限幅、p99 延迟（纯 Python 模拟）。

讲义：ros2/notes/lessons/20-policy-node.md
运行：uv run python ch20_policy_node.py
为什么是模拟：本机没有 ROS 2 也没有真模型。时间戳、动作块、延迟样本都是编的，只用来把讲义第 1–3 步的规则跑一遍。
"""

import math

STEP_S = 0.02  # 动作块每步 20 ms（讲义第 2 步：未来 50 步，每步 20 ms）
IMAGES = [0.000, 0.033, 0.066, 0.100]  # 图像时间戳，30 Hz（编的）
JOINTS = [0.002 + 0.010 * k for k in range(10)]  # 关节状态时间戳，100 Hz（编的）


def approx_sync(images: list[float], joints: list[float], slop: float) -> list[tuple[float, float]]:
    """近似时间同步：每张图配一条时间戳最近的关节状态，相差超过 slop 秒就不配。"""
    pairs = []
    for ti in images:
        tj = min(joints, key=lambda t: abs(t - ti))
        if abs(tj - ti) <= slop:
            pairs.append((ti, tj))
    return pairs


class ChunkBuffer:
    """推理写、执行读：存"最新动作块 + 它对应的起始时刻"，执行时按当前时刻算出该取第几步。"""

    def __init__(self):
        self.chunk: list[float] = []
        self.start = 0.0

    def write(self, chunk: list[float], start: float):
        self.chunk, self.start = chunk, start

    def step_at(self, now: float) -> int:
        return math.floor((now - self.start) / STEP_S + 1e-9)

    def action_at(self, now: float) -> float:
        return self.chunk[min(self.step_at(now), len(self.chunk) - 1)]


def temporal_ensemble(predictions: list[float]) -> float:
    """时间集成：同一时刻几个动作块给出的动作取平均（ACT 用指数权重，这里取等权，简化）。"""
    return sum(predictions) / len(predictions)


def limit_step(prev: float, target: float, max_delta: float) -> float:
    """限幅：每步关节变化量不超过 max_delta。"""
    return prev + max(-max_delta, min(max_delta, target - prev))


def percentile(samples: list[float], q: float) -> float:
    """第 q 百分位（最近秩法）：从小到大排，取第 ⌈q/100 · n⌉ 个。"""
    s = sorted(samples)
    return s[math.ceil(q / 100 * len(s)) - 1]


def main() -> None:
    print("\n第一步 · 近似时间同步：图像 30 Hz、关节 100 Hz，差 5 ms 以内才配对")
    for ti, tj in approx_sync(IMAGES, JOINTS, slop=0.005):
        print(f"  图像 {ti:.3f} s ↔ 关节 {tj:.3f} s（差 {abs(ti - tj) * 1000:.0f} ms）")
    print("  0.100 s 那张图没配上：最近的关节状态差了 8 ms")

    print("\n第二步 · 动作块缓冲区：块从 t=1.00 s 开始，每步 20 ms；执行回调按当前时刻取第几步")
    buf = ChunkBuffer()
    buf.write([0.10, 0.12, 0.14, 0.16, 0.18], start=1.00)  # 5 步的动作块（编的）
    for now in [1.00, 1.019, 1.02, 1.05]:
        print(f"  now={now:.3f} s → 第 {buf.step_at(now)} 步，动作 {buf.action_at(now):.2f}")

    print("\n第二步（续）· 衔接：同一时刻旧块说 0.16、新块说 0.20，时间集成取平均")
    print("  硬切换：0.16 → 0.20 一下跳 0.04；时间集成:", round(temporal_ensemble([0.16, 0.20]), 3))

    print("\n第三步 · 限幅：上一步 0.16，模型突然要 0.40，每步最多变 0.05")
    print("  实际发出:", round(limit_step(0.16, 0.40, 0.05), 3))

    print("\n第三步（续）· 测量：看平均，更要看 p99")
    latency_ms = [42, 45, 44, 41, 43, 46, 44, 120, 45, 43] * 10  # 100 个样本，每 10 个里有一个慢的（编的）
    print(f"  平均 {sum(latency_ms) / len(latency_ms):.1f} ms，p50 {percentile(latency_ms, 50)} ms，"
          f"p99 {percentile(latency_ms, 99)} ms")


if __name__ == "__main__":
    main()
