"""第 1 章代码对照：一条消息走一趟（纯 Python 模拟，不需要 rclpy）。

讲义：ros2/notes/lessons/01-what-is-ros2.md
运行：uv run python ch01_message_flow.py
为什么是模拟：本机（macOS）没有装 ROS 2，rclpy 只能在 Linux 上用二进制包装。这里用几十行 Python
把总图 2 的关键步骤（匹配、序列化、排队、spin 才叫醒回调）演一遍，数字和讲义一致。
"""

import json
from collections import deque

QUEUE_DEPTH = 10  # 讲义总图 2 第 ⑧ 步：订阅队列深度 10，满了挤掉最旧的


class Subscription:
    """一个订阅：话题名、类型、回调，外加一个深度固定的接收队列。"""

    def __init__(self, topic: str, msg_type: str, callback, depth: int = QUEUE_DEPTH):
        self.topic = topic
        self.msg_type = msg_type
        self.callback = callback
        self.queue: deque[bytes] = deque(maxlen=depth)  # maxlen：满了自动丢掉最旧的


class Graph:
    """计算图的极简版：记下所有订阅；发布时按"话题名 + 类型"匹配（QoS 第 7 章再加）。"""

    def __init__(self):
        self.subscriptions: list[Subscription] = []

    def subscribe(self, topic: str, msg_type: str, callback) -> Subscription:
        sub = Subscription(topic, msg_type, callback)
        self.subscriptions.append(sub)
        return sub

    def publish(self, topic: str, msg_type: str, msg: dict) -> int:
        """⑤–⑧：对象 → 字节（序列化），放进每个匹配上的订阅队列。返回送到了几个订阅。"""
        data = json.dumps(msg).encode()  # 真 ROS 2 用 CDR 格式，这里用 JSON 代替
        n = 0
        for sub in self.subscriptions:
            if sub.topic == topic and sub.msg_type == msg_type:
                sub.queue.append(data)
                n += 1
        return n


def spin_once(graph: Graph) -> int:
    """⑨–⑪：executor 看哪个队列有数据，取出来、字节 → 对象（反序列化），再调回调。返回调了几次。"""
    calls = 0
    for sub in graph.subscriptions:
        while sub.queue:
            msg = json.loads(sub.queue.popleft())
            sub.callback(msg)
            calls += 1
    return calls


def main() -> None:
    print("\n第一步 · 建立连接：话题名 + 类型都对上才送得到")
    g = Graph()
    heard: list[str] = []
    g.subscribe("/chatter", "std_msgs/msg/String", lambda m: heard.append(m["data"]))
    print("  发到 /chatter（String）送到", g.publish("/chatter", "std_msgs/msg/String", {"data": "Hello World: 0"}), "个订阅")
    print("  发到 /chater（拼错）送到", g.publish("/chater", "std_msgs/msg/String", {"data": "x"}), "个订阅")

    print("\n第二步 · 往下变字节：队列里存的是 bytes，不是对象")
    sub = g.subscriptions[0]
    print("  队列里的第一条:", sub.queue[0], " 类型:", type(sub.queue[0]).__name__)

    print("\n第三步 · spin 才叫醒回调")
    print("  spin 之前，回调收到", len(heard), "条")
    spin_once(g)
    print("  spin 之后，回调收到", heard)

    print("\n第四步 · 队列深度 10：不 spin 连发 12 条，最旧的 2 条被挤掉")
    heard.clear()
    for i in range(1, 13):
        g.publish("/chatter", "std_msgs/msg/String", {"data": f"Hello World: {i}"})
    print("  队列里现在有", len(sub.queue), "条")
    spin_once(g)
    print("  回调收到的第一条:", heard[0], " 最后一条:", heard[-1])


if __name__ == "__main__":
    main()
