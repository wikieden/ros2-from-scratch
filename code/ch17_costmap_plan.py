"""第 17 章代码对照：代价地图的格子、膨胀层、规划器在格子里搜一条代价最小的路（纯 Python，Dijkstra）。

讲义：ros2/notes/lessons/17-nav2.md
运行：uv run python ch17_costmap_plan.py
为什么是模拟：本机没有 Nav2。这里用一张 5 × 9 的小格子图：'#' 是障碍（被占），膨胀层给障碍周围的格子加代价，
规划器用 Dijkstra（NavFn 插件的算法之一）找总代价最小的路。膨胀代价的数是编的，只表示"离障碍越近越贵"，
不是 Nav2 膨胀层的真实公式。
"""

import heapq
import math

GRID = [
    "....#....",
    "....#....",
    "....#....",
    ".........",
    ".........",
]  # 一堵从上往下的墙；起点左上、终点右上（编的）
START, GOAL = (0, 0), (0, 8)


def obstacles(grid: list[str]) -> set[tuple[int, int]]:
    return {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "#"}


def inflate(grid: list[str], radius: float = 1.5) -> dict[tuple[int, int], float]:
    """膨胀层：离最近障碍的距离 d ≤ radius 的格子加代价，越近越贵（d=1 加 3，d=√2 加 1.5）。"""
    obs = obstacles(grid)
    cost = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (r, c) in obs:
                continue
            d = min(math.dist((r, c), o) for o in obs)
            if d <= radius:
                cost[(r, c)] = 3.0 if d <= 1 else 1.5
    return cost


def dijkstra(grid: list[str], start, goal, extra: dict) -> tuple[list[tuple[int, int]], float]:
    """上下左右走一格代价 1，再加上格子的膨胀代价；障碍格不能进。返回路径和总代价。"""
    obs = obstacles(grid)
    rows, cols = len(grid), len(grid[0])
    best = {start: 0.0}
    prev = {}
    todo = [(0.0, start)]
    while todo:
        d, cell = heapq.heappop(todo)
        if cell == goal:
            break
        if d > best[cell]:
            continue
        r, c = cell
        for nb in [(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)]:
            if not (0 <= nb[0] < rows and 0 <= nb[1] < cols) or nb in obs:
                continue
            nd = d + 1 + extra.get(nb, 0.0)
            if nd < best.get(nb, math.inf):
                best[nb], prev[nb] = nd, cell
                heapq.heappush(todo, (nd, nb))
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    return path[::-1], best[goal]


def draw(grid: list[str], path, extra: dict) -> list[str]:
    """'#' 障碍、'+' 膨胀过的格子、'*' 路径、S / G 起点终点。"""
    out = []
    on_path = set(path)
    for r, row in enumerate(grid):
        line = ""
        for c, ch in enumerate(row):
            if (r, c) == START:
                line += "S"
            elif (r, c) == GOAL:
                line += "G"
            elif (r, c) in on_path:
                line += "*"
            elif (r, c) in extra:
                line += "+"
            else:
                line += ch
        out.append(line)
    return out


def main() -> None:
    print("\n第二步 · 代价地图：'#' 被占，'+' 是膨胀层加了代价的格子")
    extra = inflate(GRID)
    for line in draw(GRID, [], extra):
        print("  ", line)

    print("\n第一步 · 规划器：没有膨胀层时，最短路贴着墙脚绕过去")
    path, cost = dijkstra(GRID, START, GOAL, {})
    for line in draw(GRID, path, {}):
        print("  ", line)
    print(f"  走了 {len(path) - 1} 格，总代价 {cost}")

    print("\n第二步（续）· 加上膨胀层：多走两格，换来离墙远一点")
    path, cost = dijkstra(GRID, START, GOAL, extra)
    for line in draw(GRID, path, extra):
        print("  ", line)
    print(f"  走了 {len(path) - 1} 格，总代价 {cost}")


if __name__ == "__main__":
    main()
