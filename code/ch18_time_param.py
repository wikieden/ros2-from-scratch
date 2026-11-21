"""第 18 章代码对照：起点修正到限位、"路径"排上时间变成"轨迹"（纯 Python 模拟，只考虑速度上限）。

讲义：ros2/notes/lessons/18-moveit2.md
运行：uv run python ch18_time_param.py
为什么是模拟：本机没有 MoveIt 2。这里用一个极简的时间参数化：每一段按"最慢的那个关节"排时间，
只管速度上限、不管加速度，所以速度在路点处会跳变。MoveIt 推荐的 TOTG 同时满足速度和加速度上限，结果更平滑。
"""

import itertools


def check_start_state_bounds(q: list[float], lower: list[float], upper: list[float]) -> list[float]:
    """CheckStartStateBounds 适配器的意思：真机读数略超出限位，就把起点截到限位上。"""
    return [min(max(x, lo), hi) for x, lo, hi in zip(q, lower, upper)]


def time_parameterize(path: list[list[float]], v_max: list[float]) -> list[dict]:
    """路径（一串关节位形，没有时间）→ 轨迹（每个点的 time_from_start 和各关节速度）。"""
    points = [{"positions": path[0], "time_from_start": 0.0, "velocities": [0.0] * len(path[0])}]
    t = 0.0
    for a, b in itertools.pairwise(path):
        dt = max(abs(qb - qa) / v for qa, qb, v in zip(a, b, v_max))  # 最慢的关节决定这一段要多久
        t += dt
        vel = [round((qb - qa) / dt, 3) for qa, qb in zip(a, b)]
        points.append({"positions": b, "time_from_start": round(t, 3), "velocities": vel})
    points[-1]["velocities"] = [0.0] * len(path[0])  # 终点停下
    return points


def main() -> None:
    print("\n第二步 ④ · 规划请求适配器：起点 1.0005 略超上限 1.0，先修正到限位")
    print("  ", check_start_state_bounds([1.0005, -0.2], [-1.0, -2.0], [1.0, 2.0]))

    print("\n第二步 ⑤ · 规划器给的是路径：只有位形，没有时间")
    path = [[0.0, 0.0], [0.5, 0.2], [0.8, 1.0]]  # 两个关节、三个路点，都是编的
    v_max = [1.0, 0.5]  # 每个关节的最高速度 rad/s（编的）
    print("  路径:", path)

    print("\n第二步 ⑤（续）· 时间参数化：每一段由最慢的关节决定要多久")
    for p in time_parameterize(path, v_max):
        print(f"  t={p['time_from_start']:<4} 位置 {p['positions']}  速度 {p['velocities']}")


if __name__ == "__main__":
    main()
