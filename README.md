# 从零学 ROS 2

**在线阅读：<https://wikieden.github.io/ros2-from-scratch/>** · [讲义目录](https://wikieden.github.io/ros2-from-scratch/lessons/index.html) · [全部动画](https://wikieden.github.io/ros2-from-scratch/animations/index.html) · [复习卡片](https://wikieden.github.io/ros2-from-scratch/review.html) · [全部讲义书](https://wikieden.github.io/ai-books/)

> 20 章 · 21 个动画（GIF + 可交互页面）· 47 张复习卡片 · 覆盖 study-plan 阶段 A–I：从 turtlesim 命令行到把学习策略部署成 ROS 2 节点；目标发行版 Lyrical Luth（2026-05 LTS）

## 这本书讲什么

从"ROS 不是操作系统，是机器人各部分之间的管道"讲起，先用 turtlesim 和 `ros2` 命令行看清节点、话题、服务、参数、动作，再自己写包和 Python 节点；接着拆开通信机制（QoS、发现与中间件、executor、零拷贝、时间与托管节点），然后是机器人本体（tf2 坐标树、URDF、launch / 测试 / 调试）、控制与应用栈（ros2_control、Nav2、MoveIt 2），最后讲仿真与部署，把一个 VLA（Vision-Language-Action：视觉 / 语言 / 动作）策略包成节点接到真机上。

- **适合谁**：会写 Python、想把学到的机器人学习模型接到真机器人上的人。不需要先会 C++ 或 Linux 系统编程；用到的坐标变换、四元数、实时调度在用到的那一章现场补。
- **读完能做什么**：看懂一个 ROS 2 系统的计算图和 launch 文件，自己写节点、接口和托管节点，选对 QoS 和 executor，配好 tf2 / URDF / ros2_control；按 study-plan 做完里程碑 R-M0–R-M10，最后一个就是"学习策略作为 ROS 2 节点跑 50 Hz 闭环"。
- **怎么读**：按章顺序读。每章先看讲解和动画，再自己做练习，最后用复习卡片隔几天考自己。

## 讲解的特点

- **一次一小步**：每个概念按"白话类比 → 命令 / 代码 / 规则（每个名字说清楚是什么）→ 小例子亲手走一遍"讲，比如 QoS 用寄快递、executor 用餐厅服务员、tf2 用家谱。
- **每章一个动画**：关键原理做成可交互页面，▶ 播放、→ 单步、↺ 从头开始；GIF 版直接嵌在正文里。
- **对照原文**：每章开头"对应原文"一行、正文里的"依据："和附录的推荐阅读，都指向本地 `ros2/materials/` 里的官方文档、设计文章和生态文档（ros2_control、Nav2、MoveIt 2、rmw_zenoh），有把握的标了行号（如 About-Domain-ID.rst L92–L110）。
- **保留真实的学习过程**：练习与作答记录里写学习时的原话、对错和点评；答错、卡住的地方变成复习卡片。
- **术语不设门槛**：缩写第一次出现就给英文全称并逐词解释（如 QoS = Quality of Service：服务 / 质量），全书缩写见 [缩写与术语表](https://wikieden.github.io/ros2-from-scratch/lessons/appendix-glossary.html)。
- **每章都有代码对照**：附录最后一节把本章的规则和数字用纯 Python 模拟一遍（本机 macOS 没有 rclpy，原因见第 1 章），配测试核对和讲义一致，顺带讲代码里才看得到的坑（列表是引用、浮点换算步数要加 1e-9、四元数用半角……）；只算讲过的例子，不提前给练习答案。每章还配了一个 Jupyter notebook（`ros2/solutions/chapter-code/notebooks/`），讲解和代码放在一起，一格一格边读边跑。
- **每章收尾有口诀**：几句话记住一章，全部口诀汇总在本页末尾。

## 示例动画

<table>
<tr>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/01-message-flow.gif" width="100%" alt="第 1 章 · 一条消息走一趟"><br><b>第 1 章 · 一条消息走一趟</b><br>发现、匹配、变字节、排队，spin 才叫醒回调<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/01-what-is-ros2.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/01-message-flow.html">▶ 交互</a></td>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/07-qos-matching.gif" width="100%" alt="第 7 章 · QoS 匹配"><br><b>第 7 章 · QoS 匹配</b><br>订阅者要求不高于发布者提供，才连得上<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/07-qos.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/07-qos-matching.html">▶ 交互</a></td>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/09-executor-timeline.gif" width="100%" alt="第 9 章 · executor 时间线"><br><b>第 9 章 · executor 时间线</b><br>一个慢回调拖垮控制回路，分组分线程救回来<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/09-executors.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/09-executor-timeline.html">▶ 交互</a></td>
</tr>
<tr>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/12-tf-tree.gif" width="100%" alt="第 12 章 · tf2 变换树"><br><b>第 12 章 · tf2 变换树</b><br>map → odom → base_link，先转后移、沿树相乘<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/12-tf2.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/12-tf-tree.html">▶ 交互</a></td>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/15-ros2-control-loop.gif" width="100%" alt="第 15 章 · ros2_control 一拍三步"><br><b>第 15 章 · ros2_control 一拍三步</b><br>read → update → write，接口就是共享变量<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/15-realtime-ros2-control.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/15-ros2-control-loop.html">▶ 交互</a></td>
<td width="33%" valign="top"><img src="https://wikieden.github.io/ros2-from-scratch/animations/20-policy-node.gif" width="100%" alt="第 20 章 · 学习策略节点"><br><b>第 20 章 · 学习策略节点</b><br>同步输入、快慢分离、动作块衔接、安全兜底<br><a href="https://wikieden.github.io/ros2-from-scratch/lessons/20-policy-node.html">讲义</a> · <a href="https://wikieden.github.io/ros2-from-scratch/animations/20-policy-node.html">▶ 交互</a></td>
</tr>
</table>

全部动画见 [动画目录](https://wikieden.github.io/ros2-from-scratch/animations/index.html)（本地看交互版要起服务，见那里的说明）。

## 目录

每章都配一个动画：**GIF** 在讲义正文里直接播放，**▶ 交互**是可以点按钮单步的页面。

| 章 | 主题 | 一句话精要 | 动画 | 卡片 | 状态 |
|---|---|---|---|---|---|
| [1](https://wikieden.github.io/ros2-from-scratch/lessons/01-what-is-ros2.html) | ROS 2 是什么：架构、消息流程、四种说话方式、为什么有 ROS 2 | 节点写在上，中间件能换插头；spin 才叫醒回调 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/01-architecture.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/01-architecture.html)；[GIF](https://wikieden.github.io/ros2-from-scratch/animations/01-message-flow.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/01-message-flow.html) | R01–R05 | 正文完成，练习 1-3、1-4 可选待做 |
| [2](https://wikieden.github.io/ros2-from-scratch/lessons/02-turtlesim-cli.html) | 用命令行看懂 turtlesim | `ros2 <对象> <动作>`：先 list、再 show、再 pub / call / set | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/02-turtlesim-graph.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/02-turtlesim-graph.html) | R06–R09 | 正文完成，练习待做 |
| [3](https://wikieden.github.io/ros2-from-scratch/lessons/03-launch-log-bag.html) | 日志、launch 和 bag | 日志五级三去处；一张清单起全家；录的是字节 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/03-launch-log-bag.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/03-launch-log-bag.html) | R10–R12 | 正文完成，练习待做 |
| [4](https://wikieden.github.io/ros2-from-scratch/lessons/04-workspace-package.html) | 工作区、colcon 和第一个包 | 先 source 底层再 source 上层；colcon 按依赖排顺序 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/04-workspace-build.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/04-workspace-build.html) | R13–R14 | 正文完成，练习待做 |
| [5](https://wikieden.github.io/ros2-from-scratch/lessons/05-python-nodes.html) | 用 Python 写节点：发布、订阅、服务、参数 | 一个节点 = 一堆回调 + 一个 spin；回调里别同步 call | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/05-python-node.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/05-python-node.html) | R15–R17 | 正文完成，练习待做 |
| [6](https://wikieden.github.io/ros2-from-scratch/lessons/06-interfaces-actions.html) | 自定义接口与动作 | 接口包只能 ament_cmake；动作 = 三服务两话题 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/06-action-internals.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/06-action-internals.html) | R18–R19 | 正文完成，练习待做 |
| [7](https://wikieden.github.io/ros2-from-scratch/lessons/07-qos.html) | QoS：通信质量设置 | 要求不高于提供才成交；不成交不报错，只是收不到 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/07-qos-matching.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/07-qos-matching.html) | R20–R21 | 正文完成，练习待做 |
| [8](https://wikieden.github.io/ros2-from-scratch/lessons/08-middleware-discovery.html) | 中间件、发现与网络 | 同号同频道；一个环境变量换中间件；Zenoh 先起路由器 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/08-discovery.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/08-discovery.html) | R22–R23 | 正文完成，练习待做 |
| [9](https://wikieden.github.io/ros2-from-scratch/lessons/09-executors.html) | Executor 与回调组 | 默认组是互斥组；多线程不分组还是串行 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/09-executor-timeline.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/09-executor-timeline.html) | R24–R25 | 正文完成，练习待做 |
| [10](https://wikieden.github.io/ros2-from-scratch/lessons/10-composition-zero-copy.html) | 组合、进程内通信与零拷贝 | 组件进容器；unique_ptr 一交，零拷贝 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/10-zero-copy.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/10-zero-copy.html) | R26–R27 | 正文完成，练习待做 |
| [11](https://wikieden.github.io/ros2-from-scratch/lessons/11-time-lifecycle.html) | 时间与托管节点 | 全体 use_sim_time；configure 准备，activate 开工 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/11-lifecycle.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/11-lifecycle.html) | R28–R29 | 正文完成，练习待做 |
| [12](https://wikieden.github.io/ros2-from-scratch/lessons/12-tf2.html) | tf2：坐标变换树 | 每个坐标系一个爹；先转后移；目标在前、源在后 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/12-tf-tree.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/12-tf-tree.html) | R30–R31 | 正文完成，练习待做 |
| [13](https://wikieden.github.io/ros2-from-scratch/lessons/13-urdf-rviz.html) | URDF、xacro、robot_state_publisher 与 RViz | URDF + 关节角 → 正运动学 → tf → RViz | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/13-urdf-pipeline.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/13-urdf-pipeline.html) | R32–R33 | 正文完成，练习待做 |
| [14](https://wikieden.github.io/ros2-from-scratch/lessons/14-launch-test-debug.html) | launch 进阶、测试与调试 | launch 是描述不是脚本；关键进程退出就全停 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/14-launch-expand.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/14-launch-expand.html) | R34–R35 | 正文完成，练习待做 |
| [15](https://wikieden.github.io/ros2-from-scratch/lessons/15-realtime-ros2-control.html) | 实时与 ros2_control 架构 | 实时 = 准时；一拍三步 read → update → write | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/15-ros2-control-loop.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/15-ros2-control-loop.html) | R36–R37 | 正文完成，练习待做 |
| [16](https://wikieden.github.io/ros2-from-scratch/lessons/16-hardware-controllers.html) | 硬件组件与控制器 | configure 通信、activate 上电；JTC 按时间插值 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/16-hardware-lifecycle.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/16-hardware-lifecycle.html) | R38–R39 | 正文完成，练习待做 |
| [17](https://wikieden.github.io/ros2-from-scratch/lessons/17-nav2.html) | Nav2：移动机器人导航栈 | 五个服务器 + 两张代价地图 + 一棵行为树 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/17-nav2-flow.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/17-nav2-flow.html) | R40–R41 | 正文完成，练习待做 |
| [18](https://wikieden.github.io/ros2-from-scratch/lessons/18-moveit2.html) | MoveIt 2：机械臂运动规划 | 路径没时间，轨迹有时间；执行交给 JTC | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/18-moveit-pipeline.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/18-moveit-pipeline.html) | R42–R43 | 正文完成，练习待做 |
| [19](https://wikieden.github.io/ros2-from-scratch/lessons/19-sim-deploy.html) | 仿真与部署 | 上层不动，只换一层；大消息 + Wi-Fi 会卡 30 秒 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/19-sim-to-real.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/19-sim-to-real.html) | R44–R45 | 正文完成，练习待做 |
| [20](https://wikieden.github.io/ros2-from-scratch/lessons/20-policy-node.html) | 收尾：把学习策略部署成 ROS 2 节点 | 推理慢、执行快，分组分线程；块间平滑、过期就停 | [GIF](https://wikieden.github.io/ros2-from-scratch/animations/20-policy-node.gif) · [▶ 交互](https://wikieden.github.io/ros2-from-scratch/animations/20-policy-node.html) | R46–R47 | 正文完成，练习待做 |

附录：[缩写与术语表](https://wikieden.github.io/ros2-from-scratch/lessons/appendix-glossary.html)。

建议顺序：第 1–6 章（会用、会写）→ 装好环境做 R-M0–R-M2 → 第 7–11 章（通信机制）→ 第 12–14 章（坐标、模型、工程化）→ 第 15–20 章（控制与应用栈）。

---

本仓库由私有学习仓库里的脚本 `tools/publish-transformer/build.py` 自动生成，内容摘自讲义目录，不要直接修改这里的文件。
