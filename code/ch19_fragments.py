"""第 19 章代码对照：大消息在 Wi-Fi 上为什么容易"卡住"——数一数 IP 分片，算一算丢一片的概率（纯 Python 计算）。

讲义：ros2/notes/lessons/19-sim-deploy.md
运行：uv run python ch19_fragments.py
为什么是模拟：这里不需要 ROS，只是算术。30 秒、256 KB 两个数来自 DDS-tuning.rst L47–L48；
64 KB 一个 UDP 包、1500 字节的 MTU（每片约 1480 字节数据）是常见网络默认值，不是 ROS 文档里的数；丢包率是编的。
"""

import math

UDP_MAX = 65_507  # 一个 UDP 包最多带的数据（字节）
IP_PAYLOAD = 1_480  # MTU 1500 减去 20 字节 IP 头
IPFRAG_TIME_S = 30  # Linux 默认等分片重组的时间（DDS-tuning.rst L47）
IPFRAG_BUFFER = 262_144  # 分片重组缓冲区默认 256 KB（DDS-tuning.rst L48、L75）


def fragments_per_datagram(size: int = UDP_MAX) -> int:
    """一个 UDP 包被拆成几片 IP 分片。"""
    return math.ceil(size / IP_PAYLOAD)


def datagram_loss(p_fragment: float, n_fragments: int) -> float:
    """任何一片丢了，整个 UDP 包就拼不回来：1 − (1 − p)^n。"""
    return 1 - (1 - p_fragment) ** n_fragments


def incomplete_datagrams_to_fill_buffer(size: int = UDP_MAX) -> float:
    """每个残缺的 UDP 包最多占着接近 size 字节，几个就能把 256 KB 缓冲区占满。"""
    return IPFRAG_BUFFER / size


def main() -> None:
    print("\n第三步 · 一张 1080p 原始图像（第 10 章：6,220,800 字节）要拆成多少片")
    image = 1920 * 1080 * 3
    n_udp = math.ceil(image / UDP_MAX)
    n_frag = fragments_per_datagram()
    print(f"  {n_udp} 个 UDP 包，每个 {n_frag} 片 IP 分片，一共约 {n_udp * n_frag} 片")

    print("\n第三步（续）· 每片只丢 1%（编的），一个 64 KB 的 UDP 包有多大概率拼不回来")
    print(f"  {datagram_loss(0.01, n_frag):.0%}")

    print("\n第三步（再续）· 拼不回来的残片占着缓冲区：多少个就占满 256 KB，占满后要等多久")
    print(f"  约 {incomplete_datagrams_to_fill_buffer():.0f} 个就满；默认要等 {IPFRAG_TIME_S} 秒才清掉")


if __name__ == "__main__":
    main()
