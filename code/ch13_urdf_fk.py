"""第 13 章代码对照：xacro 的属性和 ${} 计算、读 URDF 的 link / joint、robot_state_publisher 的正运动学（纯 Python）。

讲义：ros2/notes/lessons/13-urdf-rviz.md
运行：uv run python ch13_urdf_fk.py
为什么是模拟：本机没有 xacro 和 robot_state_publisher。xacro 这里只展开 property 和 ${算式}（不做宏）；
URDF 用标准库 xml.etree 读；正运动学用第 12 章的变换乘法，一个关节一个变换。
"""

import math
import re
import xml.etree.ElementTree as ET

from ch12_tf2 import Transform, quat_from_yaw, r3

ARM_XACRO = """
<robot name="arm" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:property name="link_len" value="0.3"/>
  <xacro:property name="forearm_len" value="0.25"/>
  <link name="base_link"/>
  <link name="upper_arm"/>
  <link name="forearm"/>
  <link name="tool"/>
  <joint name="shoulder" type="revolute">
    <parent link="base_link"/><child link="upper_arm"/>
    <origin xyz="0 0 0.1"/><axis xyz="0 0 1"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1.0"/>
  </joint>
  <joint name="elbow" type="revolute">
    <parent link="upper_arm"/><child link="forearm"/>
    <origin xyz="${link_len} 0 0"/><axis xyz="0 0 1"/>
    <limit lower="-2.0" upper="2.0" effort="10" velocity="1.0"/>
  </joint>
  <joint name="tool_mount" type="fixed">
    <parent link="forearm"/><child link="tool"/>
    <origin xyz="${forearm_len} 0 0"/>
  </joint>
</robot>
"""  # 一个平面 2 连杆臂：两段长 0.3、0.25 取自讲义第 2 步的 xacro 例子，其余数字是编的


def expand_xacro(text: str) -> str:
    """只做两件事：收集 <xacro:property>，把 ${算式} 换成算出来的数。"""
    props = {m.group(1): float(m.group(2)) for m in re.finditer(r'<xacro:property name="(\w+)" value="([^"]+)"/>', text)}
    text = re.sub(r"\s*<xacro:property[^>]*/>", "", text)
    return re.sub(r"\$\{([^}]+)\}", lambda m: f"{eval(m.group(1), {}, props):g}", text)


def read_joints(urdf: str) -> list[dict]:
    """读出每个 joint：名字、类型、父、子、origin 的 xyz、限位。"""
    root = ET.fromstring(urdf)
    joints = []
    for j in root.findall("joint"):
        lim = j.find("limit")
        joints.append({
            "name": j.get("name"), "type": j.get("type"),
            "parent": j.find("parent").get("link"), "child": j.find("child").get("link"),
            "xyz": tuple(float(v) for v in j.find("origin").get("xyz").split()),
            "limit": (float(lim.get("lower")), float(lim.get("upper"))) if lim is not None else None,
        })
    return joints


def state_publisher(joints: list[dict], joint_states: dict[str, float]):
    """robot_state_publisher：fixed 关节 → /tf_static；活动关节 → 用关节角算出变换发 /tf（这里只做绕 z 转）。"""
    tf_static, tf = {}, {}
    for j in joints:
        if j["type"] == "fixed":
            tf_static[j["child"]] = (j["parent"], Transform(j["xyz"]))
        else:
            angle = joint_states[j["name"]]
            if j["limit"]:
                angle = max(j["limit"][0], min(j["limit"][1], angle))  # revolute 有上下限
            tf[j["child"]] = (j["parent"], Transform(j["xyz"], quat_from_yaw(angle)))
    return tf_static, tf


def tool_position(joints: list[dict], joint_states: dict[str, float]):
    """正运动学：从 tool 一路乘到 base_link，得到 tool 原点在 base_link 里的位置。"""
    tf_static, tf = state_publisher(joints, joint_states)
    tree = {**tf_static, **tf}
    frame, T = "tool", Transform()
    while frame in tree:
        parent, step = tree[frame]
        T = step * T
        frame = parent
    return T.t


def main() -> None:
    print("\n第二步 · xacro：属性当常量，${} 里能算")
    urdf = expand_xacro(ARM_XACRO)
    print("  展开后 elbow 的 origin:", re.search(r'<joint name="elbow".*?<origin xyz="([^"]+)"', urdf, re.DOTALL).group(1))

    print("\n第一步 · 读 URDF：每个 joint 连一个父 link、一个子 link")
    joints = read_joints(urdf)
    for j in joints:
        print(f"  {j['name']:<10} {j['type']:<9} {j['parent']} → {j['child']}  origin={j['xyz']}  limit={j['limit']}")

    print("\n第三步 · robot_state_publisher：fixed 关节发 /tf_static，活动关节按 /joint_states 发 /tf")
    tf_static, tf = state_publisher(joints, {"shoulder": 0.0, "elbow": 0.0})
    print("  /tf_static:", list(tf_static), " /tf:", list(tf))

    print("\n第三步（续）· 正运动学：关节角一变，tool 的位置跟着变")
    for q in [(0.0, 0.0), (math.pi / 2, 0.0), (0.0, math.pi / 2)]:
        pos = tool_position(joints, {"shoulder": q[0], "elbow": q[1]})
        print(f"  shoulder={q[0]:.2f}, elbow={q[1]:.2f} → tool 在 {r3(pos)}")
    print("  超限的关节角会被截到限位：shoulder=3.0 →", r3(tool_position(joints, {"shoulder": 3.0, "elbow": 0.0})))


if __name__ == "__main__":
    main()
