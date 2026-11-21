"""第 5 章代码对照：一个节点 = 一堆回调 + 一个 spin（用纯 Python 写一个迷你 rclpy 来模拟）。

讲义：ros2/notes/lessons/05-python-nodes.md
运行：uv run python ch05_python_node.py
为什么是模拟：本机没有 rclpy。这里的 MiniNode / MiniExecutor 只模仿真 API 的形状（create_timer、
create_publisher、create_subscription、create_service、call_async、declare_parameter），时间是假的
（按事件推进，不真的 sleep），所以 0.5 秒的定时器跑 2 秒只要一眨眼。真代码见讲义第 1–4 步。
"""

import heapq
import itertools
from typing import ClassVar


class Future:
    """凭条：先拿到，结果之后才填进去；可以挂"填好以后做什么"的回调。"""

    def __init__(self):
        self.done = False
        self._result = None
        self._callbacks = []

    def set_result(self, value):
        self.done, self._result = True, value
        for cb in self._callbacks:
            cb(self)

    def result(self):
        return self._result

    def add_done_callback(self, cb):
        self._callbacks.append(cb)


class DeadlockError(RuntimeError):
    """单线程 executor 里同步等回复：回调等回复，回复等回调结束。"""


class MiniExecutor:
    """单线程 executor：手里一张按时间排的待办表，spin 时一件一件取出来调回调。"""

    def __init__(self):
        self.now = 0.0
        self._todo = []
        self._seq = itertools.count()
        self.in_callback = False

    def schedule(self, t: float, fn):
        heapq.heappush(self._todo, (t, next(self._seq), fn))

    def spin_for(self, seconds: float):
        end = self.now + seconds
        while self._todo and self._todo[0][0] <= end + 1e-9:
            t, _, fn = heapq.heappop(self._todo)
            self.now = t
            self.in_callback = True
            try:
                fn()
            finally:
                self.in_callback = False
        self.now = end

    def spin_until_future_complete(self, future: Future, timeout: float = 10.0):
        end = self.now + timeout
        while not future.done and self._todo and self._todo[0][0] <= end:
            self.spin_for(self._todo[0][0] - self.now)


class MiniNode:
    """模仿 rclpy.node.Node 的几个方法。所有节点共用一个 executor 和一张"话题 / 服务"表。"""

    topics: ClassVar[dict[str, list]] = {}
    services: ClassVar[dict[str, object]] = {}

    def __init__(self, name: str, executor: MiniExecutor):
        self.name, self.ex = name, executor
        self._params: dict[str, object] = {}
        self._post_set = []
        self.log: list[str] = []

    # —— 定时器、发布、订阅 ——
    def create_timer(self, period: float, callback):
        def fire():
            callback()
            self.ex.schedule(self.ex.now + period, fire)

        self.ex.schedule(self.ex.now + period, fire)

    def create_publisher(self, topic: str, depth: int = 10):
        node = self

        class Pub:
            def publish(self, msg):
                for cb in node.topics.get(topic, []):
                    node.ex.schedule(node.ex.now, lambda cb=cb: cb(msg))  # 不立刻调：等 spin 取出来

        return Pub()

    def create_subscription(self, topic: str, callback, depth: int = 10):
        self.topics.setdefault(topic, []).append(callback)

    # —— 服务 ——
    def create_service(self, name: str, callback):
        self.services[name] = callback

    def call_async(self, name: str, request: dict) -> Future:
        """立刻返回凭条；回复要等 executor 在 spin 里处理服务端回调后才填上。"""
        fut = Future()
        handler = self.services[name]
        self.ex.schedule(self.ex.now + 0.001, lambda: fut.set_result(handler(request, {})))
        return fut

    def call(self, name: str, request: dict):
        """同步调用：在单线程 executor 的回调里用 → 没人去处理回复，卡死。"""
        fut = self.call_async(name, request)
        if self.ex.in_callback:
            raise DeadlockError("唯一的线程正卡在这个回调里等回复，可回复要这个线程空下来才能处理")
        self.ex.spin_until_future_complete(fut)
        return fut.result()

    # —— 参数 ——
    def declare_parameter(self, name: str, default):
        self._params[name] = default

    def get_parameter(self, name: str):
        if name not in self._params:
            raise KeyError(f"参数 {name} 没声明")
        return self._params[name]

    def set_parameter(self, name: str, value) -> bool:
        """类型必须和默认值一致；成功后调 post-set 回调。返回是否成功。"""
        if name not in self._params:
            raise KeyError(f"参数 {name} 没声明")
        if type(value) is not type(self._params[name]):
            return False
        self._params[name] = value
        for cb in self._post_set:
            cb(name, value)
        return True

    def add_post_set_parameters_callback(self, cb):
        self._post_set.append(cb)


def add_two_ints(request: dict, response: dict) -> dict:
    """服务端回调：收到请求、填好回复、返回。"""
    response["sum"] = request["a"] + request["b"]
    return response


def main() -> None:
    MiniNode.topics.clear()
    MiniNode.services.clear()

    print("\n第一步 · 节点骨架：不 spin，回调一次都不跑")
    ex = MiniExecutor()
    talker = MiniNode("minimal_publisher", ex)
    pub = talker.create_publisher("topic", 10)
    counter = {"i": 0}

    def timer_callback():
        pub.publish({"data": f"Hello World: {counter['i']}"})
        counter["i"] += 1

    talker.create_timer(0.5, timer_callback)
    print("  建好定时器，还没 spin：发了", counter["i"], "条")

    print("\n第二步 · 定时器每 0.5 秒发一条，订阅者收到就记下来")
    listener = MiniNode("minimal_subscriber", ex)
    listener.create_subscription("topic", lambda msg: listener.log.append(msg["data"]), 10)
    ex.spin_for(2.0)
    print("  spin 2 秒（假时间）后，订阅者收到:", listener.log)

    print("\n第三步 · 服务：call_async 先拿凭条，spin_until_future_complete 等它填上")
    server = MiniNode("minimal_service", ex)
    server.create_service("add_two_ints", add_two_ints)
    client = MiniNode("minimal_client_async", ex)
    fut = client.call_async("add_two_ints", {"a": 41, "b": 1})
    print("  刚拿到凭条: done =", fut.done)
    ex.spin_until_future_complete(fut)
    print("  spin 之后: done =", fut.done, " sum =", fut.result()["sum"])

    print("\n第三步（续）· 在定时器回调里同步 call()：单线程 executor 卡死")
    ex2 = MiniExecutor()
    node2 = MiniNode("deadlock_demo", ex2)
    errors = []

    def bad_timer():
        try:
            node2.call("add_two_ints", {"a": 1, "b": 2})
        except DeadlockError as e:
            errors.append(str(e))

    node2.create_timer(1.0, bad_timer)
    ex2.spin_for(1.0)
    print("  卡死原因:", errors[0])

    print("\n第四步 · 参数：先声明；默认值决定类型；改成功后 post-set 回调更新成员变量")
    p = MiniNode("minimal_param_node", ex)
    p.declare_parameter("my_parameter", "world")
    p.add_post_set_parameters_callback(lambda name, value: p.log.append(f"{name} 改成了 {value}"))
    print("  get →", p.get_parameter("my_parameter"))
    print("  set 'earth' →", p.set_parameter("my_parameter", "earth"), "；post-set 回调记下:", p.log)
    print("  set 42（整数）→", p.set_parameter("my_parameter", 42), "（类型不对，被拒绝）")
    try:
        p.get_parameter("my_paramter")
    except KeyError as e:
        print("  拼错名字 →", e)


if __name__ == "__main__":
    main()
