"""第 7 章代码对照：QoS 的"要求不能高于提供"、Keep last 深度、Transient local 给晚来的人补发（纯 Python 模拟）。

讲义：ros2/notes/lessons/07-qos.md
运行：uv run python ch07_qos.py
为什么是模拟：本机没有 ROS 2 和 DDS。兼容规则就是两张表（讲义第 2 步），这里把表写成"给每个选项排个高低"的函数，
再把讲义里两张表逐行跑一遍。截止时间 / 租期的比较规则讲义里有，这里不演示（练习 7-3 自己判断）。
"""

from collections import deque
from dataclasses import dataclass

RELIABILITY = {"BEST_EFFORT": 0, "RELIABLE": 1}  # 数字越大 = 质量越高
DURABILITY = {"VOLATILE": 0, "TRANSIENT_LOCAL": 1}


@dataclass
class QoS:
    reliability: str = "RELIABLE"  # 默认配置：Keep last 10、Reliable、Volatile
    durability: str = "VOLATILE"
    depth: int = 10


SENSOR_DATA = QoS(reliability="BEST_EFFORT", depth=5)  # Sensor data 预设：Best effort、较小队列


def compatible(pub: QoS, sub: QoS) -> bool:
    """订阅者"要求"的每一项都不高于发布者"提供"的，才能连上。"""
    return (RELIABILITY[sub.reliability] <= RELIABILITY[pub.reliability]
            and DURABILITY[sub.durability] <= DURABILITY[pub.durability])


class Publisher:
    """Transient local 的发布者会留着最近 depth 条，后来加入的 Transient local 订阅者也能拿到。"""

    def __init__(self, qos: QoS):
        self.qos = qos
        self.kept = deque(maxlen=qos.depth)

    def publish(self, msg):
        if self.qos.durability == "TRANSIENT_LOCAL":
            self.kept.append(msg)

    def late_join(self, sub: QoS) -> list:
        """一个订阅者在消息发完以后才加入，它一开始能收到哪些旧消息。"""
        if not compatible(self.qos, sub):
            return []
        return list(self.kept) if sub.durability == "TRANSIENT_LOCAL" else []


def keep_last(messages: list, depth: int) -> list:
    """History = Keep last、Depth = N：没处理完的只留最近 N 条。"""
    return list(deque(messages, maxlen=depth))


def main() -> None:
    print("\n第一步 · Keep last + Depth：攒了 8 条没处理，深度 5 只留最近 5 条")
    print("  ", keep_last([f"scan{i}" for i in range(1, 9)], 5))

    print("\n第二步 · 可靠性兼容表（讲义第 2 步）")
    for p in RELIABILITY:
        for s in RELIABILITY:
            ok = compatible(QoS(reliability=p), QoS(reliability=s))
            print(f"  发布者 {p:<11} 订阅者 {s:<11} → {'✅' if ok else '❌'}")

    print("\n第二步（续）· 持久性兼容表")
    for p in DURABILITY:
        for s in DURABILITY:
            ok = compatible(QoS(durability=p), QoS(durability=s))
            print(f"  发布者 {p:<15} 订阅者 {s:<15} → {'✅' if ok else '❌'}")

    print("\n第二步（再续）· 地图的坑：地图只发一次，晚来的订阅者能不能拿到")
    map_pub = Publisher(QoS(durability="TRANSIENT_LOCAL", depth=1))
    map_pub.publish("map v1")
    print("  晚来的 Volatile 订阅者拿到:", map_pub.late_join(QoS(durability="VOLATILE")))
    print("  晚来的 Transient local 订阅者拿到:", map_pub.late_join(QoS(durability="TRANSIENT_LOCAL", depth=1)))

    print("\n第三步 · 预设配置长什么样")
    print("  默认:", QoS())
    print("  Sensor data:", SENSOR_DATA)


if __name__ == "__main__":
    main()
