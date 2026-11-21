"""第 11 章代码对照：仿真时间怎么让定时器变快变慢；托管节点的状态机走一遍（纯 Python 模拟）。

讲义：ros2/notes/lessons/11-time-lifecycle.md
运行：uv run python ch11_time_lifecycle.py
为什么是模拟：本机没有 rclpy。时间那部分用"仿真器每真实 1 秒推进几秒"来模拟 /clock；
状态机部分照讲义第 2 步的转换表写成字典，生命周期发布者在不 Active 时 publish 不会发出去。
"""


def timer_fire_wall_times(period_sim: float, sim_speed: float, wall_seconds: float) -> list[float]:
    """定时器按 ROS 时间（= /clock）触发：仿真速度是真实的 sim_speed 倍时，每次触发落在真实时间的几秒。"""
    out, k = [], 1
    while k * period_sim / sim_speed <= wall_seconds + 1e-9:
        out.append(round(k * period_sim / sim_speed, 3))
        k += 1
    return out


TRANSITIONS = {  # (主状态, 转换) → 新的主状态；讲义第 2 步的表
    ("unconfigured", "configure"): "inactive",
    ("inactive", "activate"): "active",
    ("active", "deactivate"): "inactive",
    ("inactive", "cleanup"): "unconfigured",
    ("unconfigured", "shutdown"): "finalized",
    ("inactive", "shutdown"): "finalized",
    ("active", "shutdown"): "finalized",
}


class ManagedNode:
    """托管节点：状态只能由外部下令转换；不在 active 时 publish 不会真的发出去。"""

    def __init__(self, name: str):
        self.name = name
        self.state = "unconfigured"
        self.sent: list[str] = []
        self.log: list[str] = []

    def available_transitions(self) -> list[str]:
        """ros2 lifecycle list：当前状态下能做哪些转换。"""
        return [tr for (st, tr) in TRANSITIONS if st == self.state]

    def trigger(self, transition: str) -> str:
        """ros2 lifecycle set：调 on_<转换> 回调，成功就进入新状态。"""
        new = TRANSITIONS.get((self.state, transition))
        if new is None:
            raise ValueError(f"{self.state} 状态下不能 {transition}")
        self.log.append(f"on_{transition}: {self.state} → {new}")
        self.state = new
        return new

    def publish(self, msg: str) -> bool:
        if self.state != "active":
            return False
        self.sent.append(msg)
        return True


def main() -> None:
    print("\n第一步 · 仿真时间：定时器周期 0.1 秒（ROS 时间），仿真跑得比真实慢 10 倍")
    print("  真实 3 秒内，定时器在真实时间这些时刻触发:", timer_fire_wall_times(0.1, 0.1, 3.0))
    print("  仿真跑得和真实一样快时，真实 0.3 秒内:", timer_fire_wall_times(0.1, 1.0, 0.3))

    print("\n第二步 · 托管节点：外部按顺序下令")
    node = ManagedNode("lc_talker")
    print("  刚启动:", node.state, "；能做:", node.available_transitions())
    print("  未激活时 publish →", node.publish("Lifecycle HelloWorld #1"))
    for tr in ["configure", "activate"]:
        node.trigger(tr)
    print("  configure、activate 之后:", node.state, "；publish →", node.publish("Lifecycle HelloWorld #2"))
    for tr in ["deactivate", "cleanup", "shutdown"]:
        node.trigger(tr)
    print("  回调按顺序被调用:")
    for line in node.log:
        print("   ", line)
    print("  真正发出去的消息:", node.sent)

    print("\n第三步 · 不按顺序下令会被拒绝：unconfigured 不能直接 activate")
    try:
        ManagedNode("x").trigger("activate")
    except ValueError as e:
        print("  ", e)


if __name__ == "__main__":
    main()
