"""第 3 章代码对照：日志级别、命名空间展开、bag 录放（纯 Python 模拟，不需要 rclpy）。

讲义：ros2/notes/lessons/03-launch-log-bag.md
运行：uv run python ch03_log_launch_bag.py
为什么是模拟：本机没有 ROS 2。日志过滤、名字展开、录放这三件事的规则本身很简单，用几行 Python 就能看清；
真命令（ros2 launch / ros2 bag）留到 Linux 上做里程碑 R-M1。
"""

import json

LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]  # 从低到高


def passes(level: str, threshold: str) -> bool:
    """日志器只处理不低于设定级别的消息。"""
    return LEVELS.index(level) >= LEVELS.index(threshold)


def resolve_name(name: str, namespace: str = "/", node: str = "") -> str:
    """名字展开：/ 开头是绝对名，原样；~ 开头是私有名，接在节点名后；其余是相对名，接在命名空间后。"""
    ns = "/" + namespace.strip("/") if namespace.strip("/") else ""
    if name.startswith("/"):
        return name
    if name.startswith("~"):
        return f"{ns}/{node}{name[1:]}"
    return f"{ns}/{name}"


def record(messages: list[tuple[float, str, dict]]) -> list[tuple[float, str, bytes]]:
    """录：(时间, 话题, 消息) → (时间, 话题, 序列化后的字节)。录的时候不用反序列化，所以省 CPU。"""
    return [(t, topic, json.dumps(msg).encode()) for t, topic, msg in messages]


def play(bag: list[tuple[float, str, bytes]], rate: float = 1.0) -> list[tuple[float, str, dict]]:
    """放：按原来的时间间隔重新发出去；rate=2 就是两倍速，间隔减半。返回 (回放后第几秒发出, 话题, 消息)。"""
    t0 = bag[0][0]
    return [(round((t - t0) / rate, 3), topic, json.loads(data)) for t, topic, data in bag]


def main() -> None:
    print("\n第一步 · 日志级别：设成 INFO，DEBUG 就不打了")
    for level in LEVELS:
        print(f"  {level:<5} 在 INFO 下 → {'打印' if passes(level, 'INFO') else '丢掉'}")

    print("\n第二步 · launch 的 namespace：相对名自动加前缀")
    for ns in ["turtlesim1", "turtlesim2"]:
        print(f"  namespace={ns}: turtle1/cmd_vel → {resolve_name('turtle1/cmd_vel', ns)}")
    print("  绝对名 /rosout 不受命名空间影响 →", resolve_name("/rosout", "turtlesim1"))
    print("  私有名 ~/set_parameters（节点 sim）→", resolve_name("~/set_parameters", "turtlesim1", "sim"))

    print("\n第三步 · bag：录成字节，按原节奏放；rate=2 两倍速")
    raw = [(10.0, "/turtle1/cmd_vel", {"linear": {"x": 2.0}}),
           (10.5, "/turtle1/cmd_vel", {"angular": {"z": 1.8}}),
           (12.0, "/turtle1/cmd_vel", {"linear": {"x": -2.0}})]  # 三条指令和时间是编的
    bag = record(raw)
    print("  录下的第一条:", bag[0])
    print("  原速回放:", [(t, m) for t, _, m in play(bag)])
    print("  两倍速回放的时间:", [t for t, _, _ in play(bag, rate=2.0)])


if __name__ == "__main__":
    main()
