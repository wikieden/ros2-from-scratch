"""第 6 章代码对照：读懂 .msg 的每一行、动作底层的 5 个名字、Fibonacci 动作和目标状态机（纯 Python 模拟）。

讲义：ros2/notes/lessons/06-interfaces-actions.md
运行：uv run python ch06_interfaces_actions.py
为什么是模拟：本机没有 rosidl 和 rclpy。这里用一个小解析器按接口文档的规则拆 .msg 行，
用一个字典写下讲义总图里的目标状态机，只走"成功"和"服务端放弃"两条路（取消那条留给练习 6-3）。
"""

import re

LINE = re.compile(
    r"^(?P<type>[\w/]+?)(?P<bound_str><=\d+)?(?P<array>\[(?P<cap><=)?(?P<n>\d*)\])?\s+"
    r"(?P<name>\w+)(?:\s*=\s*(?P<const>.+)|\s+(?P<default>.+))?$"
)


def parse_field(line: str) -> dict:
    """一行 "类型 名字 [默认值]" 或 "类型 名字=常量"，拆成字典。"""
    m = LINE.match(line.split("#")[0].strip())
    if not m:
        raise ValueError(line)
    d = m.groupdict()
    out = {"类型": d["type"], "名字": d["name"]}
    if d["bound_str"]:
        out["字符串上限"] = int(d["bound_str"][2:])
    if d["array"]:
        n = d["n"]
        out["数组"] = f"最多 {n} 个" if d["cap"] else (f"正好 {n} 个" if n else "不限长度")
    if d["const"] is not None:
        out["常量"] = d["const"].strip('"')
    elif d["default"] is not None:
        out["默认值"] = d["default"].strip('"')
    return out


def action_parts(action: str) -> list[tuple[str, str]]:
    """一个动作在底层 = 3 个服务 + 2 个话题，名字都藏在 _action/ 下面。"""
    base = f"{action}/_action"
    return [(f"{base}/send_goal", "服务"), (f"{base}/cancel_goal", "服务"), (f"{base}/get_result", "服务"),
            (f"{base}/feedback", "话题"), (f"{base}/status", "话题")]


def fibonacci_execute(order: int) -> tuple[list[list[int]], list[int]]:
    """官方 server 的 execute_callback：每算出一项发一次反馈，最后返回整列。"""
    sequence = [0, 1]
    feedbacks = []
    for i in range(1, order):
        sequence.append(sequence[i] + sequence[i - 1])
        feedbacks.append(list(sequence))
    return feedbacks, sequence


TRANSITIONS = {  # 讲义总图：目标状态机，(当前状态, 事件) → 下一个状态
    ("ACCEPTED", "execute"): "EXECUTING",
    ("EXECUTING", "succeed"): "SUCCEEDED",
    ("EXECUTING", "abort"): "ABORTED",
    ("ACCEPTED", "cancel_goal"): "CANCELING",
    ("EXECUTING", "cancel_goal"): "CANCELING",
    ("CANCELING", "canceled"): "CANCELED",
}
TERMINAL = {"SUCCEEDED", "ABORTED", "CANCELED"}


def run_goal(events: list[str]) -> list[str]:
    """从 ACCEPTED 出发，按事件一路走；走到终态就停。不合法的事件直接报错。"""
    state, path = "ACCEPTED", ["ACCEPTED"]
    for ev in events:
        if state in TERMINAL:
            break
        state = TRANSITIONS[(state, ev)]
        path.append(state)
    return path


def main() -> None:
    print("\n第一步 · .msg 每行是\"类型 名字\"，后面可以跟默认值或常量")
    for line in ["int32[] unbounded_integer_array", "int32[5] five_integers_array",
                 "int32[<=5] up_to_five_integers_array", "string<=10 up_to_ten_characters",
                 "uint8 x 42", 'string full_name "John Doe"', "int32 X=123",
                 "geometry_msgs/Point center"]:
        print(f"  {line:<38} → {parse_field(line)}")

    print("\n总图 · 动作 /fibonacci 在底层是这 5 个名字")
    for name, kind in action_parts("/fibonacci"):
        print(f"  {kind}  {name}")

    print("\n第三步 · Fibonacci 动作：order=5，每算一项发一次反馈")
    feedbacks, result = fibonacci_execute(5)
    for fb in feedbacks:
        print("  反馈:", fb)
    print("  结果:", result)

    print("\n第三步（续）· 目标状态机：成功和服务端放弃两条路")
    print("  ", " → ".join(run_goal(["execute", "succeed"])))
    print("  ", " → ".join(run_goal(["execute", "abort"])))


if __name__ == "__main__":
    main()
