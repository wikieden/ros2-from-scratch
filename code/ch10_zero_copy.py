"""第 10 章代码对照：一张 1080p 图像多大、每秒搬多少；"复印一份"和"把原件递过去"在 Python 里的样子（纯模拟）。

讲义：ros2/notes/lessons/10-composition-zero-copy.md
运行：uv run python ch10_zero_copy.py
为什么是模拟：组件、进程内通信、unique_ptr 都是 C++ 的东西，本机也没有 ROS 2。这里用 Python 的 bytearray 当图像，
用 id()（对象身份号，相当于 C++ 里打印的地址）看两边拿到的是不是同一块内存。
"""


def image_bytes(width: int = 1920, height: int = 1080, channels: int = 3) -> int:
    """RGB 图像每个像素 3 个字节。"""
    return width * height * channels


class Handoff:
    """进程内通信的样子：发布者把消息"交出去"（自己的引用清空），订阅者拿到同一个对象。"""

    def __init__(self):
        self.msg = None

    def publish_move(self, holder: dict, key: str):
        self.msg = holder.pop(key)  # 相当于 publish(std::move(msg))：交出以后发布者手里就没有了
        return self.msg


def deliver(msg: bytearray, n_subscribers: int) -> list[bytearray]:
    """多个订阅者都要能改的话：最后一个拿原件，前面的各拿一份复制（讲义第 2 步）。"""
    return [bytearray(msg) for _ in range(n_subscribers - 1)] + [msg]


def main() -> None:
    print("\n总图 · 一张 1920×1080 的 RGB 图像有多大")
    size = image_bytes()
    print(f"  {size:,} 字节 ≈ {size / 1e6:.1f} MB；30 Hz 每秒 {size * 30 / 1e6:.0f} MB")

    print("\n第二步 · 复制 vs 交出：看两边拿到的是不是同一块内存")
    img = bytearray(size)
    copy = bytes(img)  # 普通跨进程：序列化 / 反序列化，等于复印一份
    print("  复印一份：同一个对象吗？", copy is img)
    holder = {"msg": img}
    received = Handoff().publish_move(holder, "msg")
    print("  交出原件：同一个对象吗？", received is img, "；发布者手里还剩", list(holder))

    print("\n第二步（续）· 三个订阅者：前两个各复制一份，最后一个拿原件")
    got = deliver(img, 3)
    print("  谁拿的是原件:", [g is img for g in got])


if __name__ == "__main__":
    main()
