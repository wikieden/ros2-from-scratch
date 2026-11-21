"""第 8 章代码对照：Domain ID 怎么算出 UDP 端口、为什么上限是 232、Linux 上为什么建议 0–101（纯 Python 计算）。

讲义：ros2/notes/lessons/08-middleware-discovery.md
运行：uv run python ch08_domain_ports.py
为什么是模拟：本机没有 DDS。端口公式只是加减乘，官方文档 About-Domain-ID.rst L88–L110 给了一串例子，
这里逐个算出来核对。公式里的 7400、250、10、2 是 DDS 规范（RTPS）的默认常数，文档本身只链接了外部说明。
"""

PB, DG, PG, D_UNICAST = 7400, 250, 2, 10  # 端口基数、每个域占的端口段长、每个参与者占几个端口、单播偏移
MAX_PORT = 65535
LINUX_EPHEMERAL = (32768, 60999)  # About-Domain-ID.rst L65：Linux 默认临时端口段


def multicast_ports(domain: int) -> tuple[int, int]:
    """一个域的发现组播端口和用户数据组播端口。"""
    base = PB + DG * domain
    return base, base + 1


def unicast_ports(domain: int, participant: int) -> tuple[int, int]:
    """同一台电脑上第 participant 个 ROS 2 进程（从 0 数）用的两个单播端口。"""
    base = PB + DG * domain + D_UNICAST + PG * participant
    return base, base + 1


def max_domain() -> int:
    """组播端口不能超过 65535：7400 + 250 × d ≤ 65535。"""
    return (MAX_PORT - PB) // DG


def max_participants(domain: int, limit: int) -> int:
    """单播端口不越过 limit（临时端口段起点或 65535）时，最多能开几个进程。"""
    p = 0
    while unicast_ports(domain, p)[1] < limit:
        p += 1
    return p


def main() -> None:
    print("\n第一步 · 组播端口：7400 + 250 × 域号（文档 L92–L93）")
    for d in [0, 1, 2, 7]:
        print(f"  域 {d}: 组播端口 {multicast_ports(d)}")

    print("\n第一步（续）· 单播端口：每多一个进程往后挪 2 个（文档 L94–L96）")
    for p in [0, 119, 120]:
        print(f"  域 1 第 {p} 号参与者: {unicast_ports(1, p)}")
    print("  域 1 的第 120 号已经撞上域 2 的组播端口", multicast_ports(2))

    print("\n第一步（再续）· 域号上限：", max_domain(), "（文档 L50）")

    print("\n第一步（又续）· Linux 上域 101：第 53 号和第 54 号进程（文档 L102–L107）")
    print("  第 53 号:", multicast_ports(101), unicast_ports(101, 53))
    print("  第 54 号:", multicast_ports(101), unicast_ports(101, 54), "← 进了临时端口段", LINUX_EPHEMERAL)
    print("  域 101 最多开", max_participants(101, LINUX_EPHEMERAL[0]), "个进程；域 232 最多开",
          max_participants(232, MAX_PORT + 1), "个（文档 L109–L110）")


if __name__ == "__main__":
    main()
