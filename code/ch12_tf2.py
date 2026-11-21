"""第 12 章代码对照：四元数、"先旋转后平移"、变换相乘、沿着树查变换、按时间插值（纯 Python，不需要 tf2）。

讲义：ros2/notes/lessons/12-tf2.md
运行：uv run python ch12_tf2.py
为什么是模拟：本机没有 tf2_ros。这里只用 math 写四元数和变换，算的是讲义第 1 步的两个数字例子；
树查询和时间缓冲按讲义第 2 步的规则写成小函数。真代码里这些由 tf2 的 Buffer.lookup_transform 完成。
"""

import itertools
import math

Vec = tuple[float, float, float]
Quat = tuple[float, float, float, float]  # (x, y, z, w)，w 是实部
IDENTITY: Quat = (0.0, 0.0, 0.0, 1.0)  # 不转


def quat_from_yaw(yaw: float) -> Quat:
    """只绕 z 轴转 yaw 弧度（平面机器人最常用）：(0, 0, sin(yaw/2), cos(yaw/2))。"""
    return (0.0, 0.0, math.sin(yaw / 2), math.cos(yaw / 2))


def quat_mul(a: Quat, b: Quat) -> Quat:
    """四元数乘法：先转 b 再转 a。"""
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz)


def quat_conj(q: Quat) -> Quat:
    """单位四元数的逆 = 共轭：虚部取负。"""
    return (-q[0], -q[1], -q[2], q[3])


def rotate(q: Quat, v: Vec) -> Vec:
    """用四元数转一个向量：q · (v, 0) · q⁻¹。"""
    x, y, z, _ = quat_mul(quat_mul(q, (*v, 0.0)), quat_conj(q))
    return (x, y, z)


class Transform:
    """父坐标系 ← 子坐标系：子坐标系的原点在父坐标系里的位置 t，加上朝向 q。"""

    def __init__(self, t: Vec = (0.0, 0.0, 0.0), q: Quat = IDENTITY):
        self.t, self.q = t, q

    def apply(self, p: Vec) -> Vec:
        """P_父 = T · P_子：先旋转，后平移。"""
        r = rotate(self.q, p)
        return (r[0] + self.t[0], r[1] + self.t[1], r[2] + self.t[2])

    def __mul__(self, other: "Transform") -> "Transform":
        """_B T_A = _B T_E · _E T_A：先用右边的，再用左边的。"""
        return Transform(self.apply(other.t), quat_mul(self.q, other.q))

    def inverse(self) -> "Transform":
        qi = quat_conj(self.q)
        t = rotate(qi, self.t)
        return Transform((-t[0], -t[1], -t[2]), qi)


def lookup(tree: dict[str, tuple[str, Transform]], target: str, source: str) -> Transform:
    """tree[子] = (父, 父←子)。沿树往上找共同祖先，把一路的变换乘起来（需要时取逆）。返回 目标←源。"""

    def to_root(frame: str) -> list[str]:
        chain = [frame]
        while chain[-1] in tree:
            chain.append(tree[chain[-1]][0])
        return chain

    up_s, up_t = to_root(source), to_root(target)
    common = next(f for f in up_s if f in up_t)
    root_from_source = Transform()
    for f in up_s[: up_s.index(common)]:  # 源 → 共同祖先
        root_from_source = tree[f][1] * root_from_source
    root_from_target = Transform()
    for f in up_t[: up_t.index(common)]:
        root_from_target = tree[f][1] * root_from_target
    return root_from_target.inverse() * root_from_source


def interpolate(buffer: list[tuple[float, float]], t: float) -> float:
    """按时间缓存的一个量（这里只缓存 x 平移）：在前后两条记录之间线性插值；超出范围就报错。"""
    times = [s for s, _ in buffer]
    if t > times[-1]:
        raise LookupError(f"extrapolation into the future：要 {t}，最新只有 {times[-1]}")
    if t < times[0]:
        raise LookupError(f"extrapolation into the past：要 {t}，最早只有 {times[0]}")
    for (t0, x0), (t1, x1) in itertools.pairwise(buffer):
        if t0 <= t <= t1:
            return x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    return buffer[-1][1]


def r3(v) -> tuple:
    """保留 3 位小数，去掉 -0.0，方便看。"""
    return tuple(round(x, 3) + 0.0 for x in v)


def main() -> None:
    print("\n第一步 · 不转的四元数是 (0, 0, 0, 1)；绕 z 转 90° 是 (0, 0, sin45°, cos45°)")
    print("  ", IDENTITY, "；", r3(quat_from_yaw(math.pi / 2)))

    print("\n第一步（续）· 相机在底座前 0.1 m、上 0.3 m，没转；杯子在相机前方 0.5 m")
    base_T_camera = Transform((0.1, 0.0, 0.3))
    print("  P_base =", r3(base_T_camera.apply((0.5, 0.0, 0.0))))

    print("\n第一步（再续）· 同一个相机朝左转 90°：先旋转、后平移")
    base_T_camera_yaw = Transform((0.1, 0.0, 0.3), quat_from_yaw(math.pi / 2))
    print("  先转:", r3(rotate(base_T_camera_yaw.q, (0.5, 0.0, 0.0))), "→ 再加平移:",
          r3(base_T_camera_yaw.apply((0.5, 0.0, 0.0))))

    print("\n第一步（又续）· 变换相乘：_B T_A = _B T_E · _E T_A")
    E_T_A = Transform((1.0, 0.0, 0.0), quat_from_yaw(math.pi / 2))
    B_T_E = Transform((0.0, 2.0, 0.0))  # 两个变换是编的
    B_T_A = B_T_E * E_T_A
    p = (1.0, 0.0, 0.0)
    print("  一步到位:", r3(B_T_A.apply(p)), "；分两步:", r3(B_T_E.apply(E_T_A.apply(p))))

    print("\n第二步 · REP 105 的树：map → odom → base_link → camera_link，查 map ← camera_link")
    tree = {
        "odom": ("map", Transform((2.0, 1.0, 0.0))),  # 定位修正（编的）
        "base_link": ("odom", Transform((3.0, 0.0, 0.0), quat_from_yaw(math.pi / 2))),  # 里程计（编的）
        "camera_link": ("base_link", Transform((0.1, 0.0, 0.3))),  # 安装位置：第一步的数
    }
    map_T_cam = lookup(tree, "map", "camera_link")
    print("  相机原点在 map 里:", r3(map_T_cam.t))
    print("  反过来查 camera_link ← map，再乘回去是不是单位变换:",
          r3((lookup(tree, "camera_link", "map") * map_T_cam).t))

    print("\n第二步（续）· 时间缓冲：x 在 t=1.0 是 0.0，在 t=2.0 是 1.0")
    buf = [(1.0, 0.0), (2.0, 1.0)]
    print("  t=1.5 →", interpolate(buf, 1.5))
    for t in [2.1, 0.5]:
        try:
            interpolate(buf, t)
        except LookupError as e:
            print(f"  t={t} →", e)


if __name__ == "__main__":
    main()
