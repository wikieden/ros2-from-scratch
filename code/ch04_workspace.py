"""第 4 章代码对照：overlay 找包的顺序、colcon 的编译顺序、entry_points 怎么变成命令（纯 Python 模拟）。

讲义：ros2/notes/lessons/04-workspace-package.md
运行：uv run python ch04_workspace.py
为什么是模拟：本机没有 ROS 2 和 colcon。这里把三条规则写成函数：source 之后按"上层先、底层后"找包；
colcon 按 package.xml 的依赖排顺序、没依赖关系的并行；setup.py 的 console_scripts 一行变成一个可执行文件名。
"""


def find_package(name: str, layers: list[tuple[str, set[str]]]) -> str | None:
    """layers 按 source 后的优先级排好：最后 source 的工作区排最前。返回包是从哪一层找到的。"""
    for layer_name, packages in layers:
        if name in packages:
            return layer_name
    return None


def build_order(deps: dict[str, set[str]]) -> list[list[str]]:
    """colcon 的排法：每一轮把"依赖都已编完"的包挑出来一起编（同一轮的可以并行）。"""
    done: set[str] = set()
    rounds = []
    while len(done) < len(deps):
        ready = sorted(p for p, d in deps.items() if p not in done and d <= done)
        if not ready:
            raise ValueError("依赖有环，排不出顺序")
        rounds.append(ready)
        done |= set(ready)
    return rounds


def parse_entry_point(line: str) -> dict:
    """'my_node = my_package.my_node:main' → 命令名、模块路径、函数名。"""
    command, target = (s.strip() for s in line.split("="))
    module, func = target.split(":")
    return {"ros2 run 用的名字": command, "模块": module, "函数": func}


def main() -> None:
    print("\n第一步 · overlay 在上、underlay 在下：同名包先找上层")
    underlay = ("/opt/ros/lyrical", {"rclpy", "turtlesim", "demo_nodes_py"})
    overlay = ("~/ros2_ws/install", {"my_package", "demo_nodes_py"})  # 假设你在上层改了一份 demo_nodes_py
    layers = [overlay, underlay]  # 先 source 底层、再 source 上层 → 上层排在前面
    for pkg in ["my_package", "demo_nodes_py", "rclpy"]:
        print(f"  {pkg:<14} 来自 {find_package(pkg, layers)}")

    print("\n第二步 · colcon 按依赖排顺序：A 依赖 B 就先编 B，互不依赖的同一轮并行")
    deps = {
        "robot_msgs": set(),
        "robot_description": set(),
        "robot_driver": {"robot_msgs"},
        "robot_bringup": {"robot_driver", "robot_description"},
    }  # 四个包的名字和依赖是编的
    for i, rnd in enumerate(build_order(deps), 1):
        print(f"  第 {i} 轮: {rnd}")

    print("\n第三步 · setup.py 的 entry_points：一行登记一个可执行文件")
    print(" ", parse_entry_point("my_node = my_package.my_node:main"))


if __name__ == "__main__":
    main()
