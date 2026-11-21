"""第 14 章代码对照：launch 文件是"描述"不是"脚本"——替换（substitution）要等启动时才代入（纯 Python 模拟）。

讲义：ros2/notes/lessons/14-launch-test-debug.md
运行：uv run python ch14_launch_subst.py
为什么是模拟：本机没有 launch / launch_ros。这里用几个小类模仿 LaunchConfiguration、PathJoinSubstitution、
PythonExpression、PushRosNamespace：写的时候只是占位，launch() 时才按命令行参数和默认值算出真值。
条件（IfCondition）和事件处理器留给练习 14-1、14-2，这里不演示。
"""


class LaunchConfiguration:
    """占位：launch 参数 name 的值，启动时才知道。"""

    def __init__(self, name: str):
        self.name = name

    def perform(self, ctx: dict) -> str:
        return ctx[self.name]


class PathJoinSubstitution:
    """把几段（可以含占位）拼成路径。"""

    def __init__(self, parts: list):
        self.parts = parts

    def perform(self, ctx: dict) -> str:
        return "/".join(resolve(p, ctx) for p in self.parts)


class PythonExpression:
    """启动时把几段拼成一个 Python 表达式再求值。"""

    def __init__(self, parts: list):
        self.parts = parts

    def perform(self, ctx: dict) -> str:
        return str(eval("".join(resolve(p, ctx) for p in self.parts), {}, {}))


def resolve(value, ctx: dict) -> str:
    """字符串原样，占位就调 perform。"""
    return value.perform(ctx) if hasattr(value, "perform") else value


def launch(description: list[dict], declared: dict[str, str], cli: dict[str, str], namespace: str = "") -> list[str]:
    """ros2 launch：先定参数（命令行 > 默认值），再把每个 Node 的占位全部算出来。返回每个节点的完整名字。"""
    ctx = {**declared, **cli}
    out = []
    for node in description:
        ns = "/".join(s for s in [namespace.strip("/"), resolve(node.get("namespace", ""), ctx).strip("/")] if s)
        extra = {k: resolve(v, ctx) for k, v in node.items() if k not in ("namespace", "name")}
        out.append(f"/{ns}/{node['name']}" if ns else f"/{node['name']}")
        if extra:
            out[-1] += f"  {extra}"
    return out


def main() -> None:
    turtlesim_ns = LaunchConfiguration("turtlesim_ns")
    description = [{"namespace": turtlesim_ns, "name": "sim"}]  # Node(namespace=turtlesim_ns, name='sim')
    declared = {"turtlesim_ns": "turtlesim1"}  # DeclareLaunchArgument('turtlesim_ns', default_value='turtlesim1')

    print("\n总图 · 写下来的时候只是占位，不是值")
    print("  description 里的 namespace 是:", type(description[0]["namespace"]).__name__)

    print("\n第一步 · 启动时才代入：默认值 vs 命令行 turtlesim_ns:=robot7")
    print("  默认:", launch(description, declared, {}))
    print("  turtlesim_ns:=robot7:", launch(description, declared, {"turtlesim_ns": "robot7"}))

    print("\n第一步（续）· 包含另一个 launch 并传参：launch_arguments={'turtlesim_ns': 'turtlesim2'}")
    print("  ", launch(description, declared, {"turtlesim_ns": "turtlesim2"}))

    print("\n第一步（再续）· GroupAction + PushRosNamespace('robot1')：整组再套一层命名空间")
    print("  ", launch(description, declared, {}, namespace="robot1"))

    print("\n第一步（又续）· PathJoinSubstitution 和 PythonExpression 也是启动时才算")
    node = {"name": "loader",
            "params_file": PathJoinSubstitution(["/opt/ros/lyrical/share", LaunchConfiguration("pkg"), "config", "a.yaml"]),
            "scale": PythonExpression([LaunchConfiguration("base_speed"), " * 2"])}  # 参数名和值是编的
    print("  ", launch([node], {"pkg": "my_robot", "base_speed": "0.5"}, {}))


if __name__ == "__main__":
    main()
