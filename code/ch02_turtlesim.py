"""第 2 章代码对照：把 turtlesim 命令行里看到的东西用 Python 算一遍（纯模拟，不需要 rclpy）。

讲义：ros2/notes/lessons/02-turtlesim-cli.md
运行：uv run python ch02_turtlesim.py
为什么是模拟：本机没有 ROS 2。这里只算"消息类型名怎么拆""YAML 里没写的字段是多少""Twist 让乌龟走出什么弧"
"动作反馈怎么一路变小"这几件事，命令本身要到装好 ROS 2 的 Linux 上敲（里程碑 R-M1）。
"""

import math

TWIST_DEFAULT = {"linear": {"x": 0.0, "y": 0.0, "z": 0.0}, "angular": {"x": 0.0, "y": 0.0, "z": 0.0}}


def split_type_name(name: str) -> dict:
    """消息类型名三段：包名 / 种类（msg、srv、action）/ 类型名。"""
    package, kind, type_name = name.split("/")
    assert kind in ("msg", "srv", "action"), kind
    return {"包名": package, "种类": kind, "类型名": type_name}


def fill_defaults(partial: dict, default: dict) -> dict:
    """`ros2 topic pub` 的 YAML 只写要改的字段，其余取默认值 0。"""
    out = {}
    for key, value in default.items():
        if isinstance(value, dict):
            out[key] = fill_defaults(partial.get(key, {}), value)
        else:
            out[key] = float(partial.get(key, value))
    return out


def drive(pose: tuple[float, float, float], twist: dict, seconds: float, dt: float = 0.001):
    """平面小乌龟：每一小步按朝向前进 linear.x·dt，再转 angular.z·dt。返回 (x, y, theta)。"""
    x, y, th = pose
    v, w = twist["linear"]["x"], twist["angular"]["z"]
    for _ in range(round(seconds / dt)):
        x += v * math.cos(th) * dt
        y += v * math.sin(th) * dt
        th += w * dt
    return x, y, th


def rotate_absolute(theta_now: float, theta_goal: float, step: float = 0.8):
    """动作 RotateAbsolute 的模拟：每次转一小步，发反馈 remaining（还差多少），最后返回结果 delta。"""
    feedbacks = []
    start = theta_now
    while abs(theta_goal - theta_now) > 1e-9:
        remaining = theta_goal - theta_now
        feedbacks.append(round(remaining, 2))
        theta_now += max(-step, min(step, remaining))  # 一步最多转 step 弧度
    return feedbacks, round(abs(theta_now - start), 2)


def main() -> None:
    print("\n第一步 · 类型名三段：包名 / 种类 / 类型名")
    for name in ["geometry_msgs/msg/Twist", "turtlesim_msgs/srv/Spawn", "turtlesim_msgs/action/RotateAbsolute"]:
        print(" ", name, "→", split_type_name(name))

    print("\n第二步 · topic pub 只写要改的字段，其余是 0")
    cmd = fill_defaults({"linear": {"x": 2.0}, "angular": {"z": 1.8}}, TWIST_DEFAULT)
    print("  \"{linear: {x: 2.0}, angular: {z: 1.8}}\" →", cmd)

    print("\n第二步（续）· 这条 Twist 让乌龟边走边转，画出一段弧")
    x, y, th = drive((0.0, 0.0, 0.0), cmd, seconds=1.0)
    print(f"  从原点朝 x 方向出发，走 1 秒：x={x:.3f}, y={y:.3f}, 朝向={th:.3f} rad（= 1.8 × 1 秒）")
    r = 2.0 / 1.8
    print(f"  解析解：半径 v/ω = {r:.3f}，x = r·sin(1.8) = {r * math.sin(1.8):.3f}，y = r·(1−cos 1.8) = {r * (1 - math.cos(1.8)):.3f}")

    print("\n第三步 · 弧度和角度：1.57 ≈ π/2 = 90°")
    print(f"  -1.57 rad = {math.degrees(-1.57):.1f}°；π/2 = {math.pi / 2:.4f}")

    print("\n第四步 · 动作：目标 theta=-1.57，反馈 remaining 一路变小，结果 delta 是实际转过的角度")
    feedbacks, delta = rotate_absolute(1.55, -1.57)  # 起始朝向 1.55 是编的，让第一条反馈接近讲义里的 -3.12
    print("  反馈:", feedbacks)
    print("  结果 delta:", delta)


if __name__ == "__main__":
    main()
