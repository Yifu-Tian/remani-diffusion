# REMANI + MPD Integration Progress / 集成进度记录

Last Updated / 最后更新: 2026-04-01  
Owner / 负责人: yifu + Codex  
Workspace / 工作空间: `/home/yifu/remani_ws/remani_mpd_ws`

## 1) Goal / 目标
Integrate diffusion-based manipulator planning into REMANI in a staged, safe way.  
以“分阶段、可回退”的方式，把 diffusion 机械臂规划接入 REMANI。

- Keep traditional base planning.  
  保留现有底盘（base）传统规划链路。
- Use base trajectory as condition for diffusion arm planning.  
  将底盘时序轨迹作为 diffusion 机械臂规划条件。
- Fall back to traditional pipeline if diffusion fails.  
  diffusion 失败时自动回退到传统 pipeline。
- Allow feedback-triggered base replan when arm planning repeatedly fails.  
  机械臂规划连续失败时，触发底盘重规划并重试。

## 2) Agreed Technical Direction / 已确认技术路线
We agreed to use a layered strategy (not end-to-end replacement).  
我们确认采用分层方案（不是端到端全替换）。

1. Traditional base planner stays as-is.  
   传统底盘规划保持不变。
2. Diffusion generates arm trajectory (or arm prior) conditioned on base trajectory.  
   diffusion 基于底盘轨迹生成机械臂轨迹（或先验）。
3. Existing optimizer validates/refines with current collision and feasibility costs.  
   现有优化器继续做碰撞/可行性校验与修正。
4. On failure, fallback to original traditional initialization and optimization.  
   失败则回退到原始初始化与优化。
5. On repeated failure, trigger base replan and retry.  
   连续失败时触发底盘重规划并重试。

Why this direction / 选择该路线原因:
- Lower risk and faster landing.  
  风险更低，上线更快。
- Preserves existing real-time and safety logic in REMANI.  
  保留 REMANI 的实时性与安全逻辑。
- Avoids immediate high-dimensional joint base+arm diffusion complexity.  
  避免一开始就处理 base+arm 高维联合生成难题。
- Supports incremental rollout and A/B evaluation.  
  便于渐进迭代与 A/B 对比评估。

## 3) Workspace Decisions and Cleanup Done / 工作空间整理结果
- Final active workspace: `/home/yifu/remani_ws/remani_mpd_ws`  
  最终主工作空间为 `remani_mpd_ws`。
- Source layout now / 当前源码结构:
  - `src/REMANI-Planner`
  - `src/mpd-public`
- Old typo link `remain_mpd_ws` has been removed.  
  拼写错误目录 `remain_mpd_ws` 已删除。
- `/home/yifu/remani_ws/src/REMANI-Planner` is now a symlink to:  
  `/home/yifu/remani_ws/src/REMANI-Planner` 现为软链接，指向:
  - `/home/yifu/remani_ws/remani_mpd_ws/src/REMANI-Planner`
- mpd source currently comes from local zip:  
  当前 mpd 来源为本地 zip 解压:
  - `/home/yifu/remani_ws/mpd-public-main.zip`
  - extracted to `src/mpd-public`

## 4) Key Code Touchpoints (Confirmed) / 关键改造入口（已确认）
- FSM orchestration / 状态机调度:
  - `src/REMANI-Planner/remani_planner/plan_manage/src/remani_replan_fsm.cpp`
- Planner manager / 规划管理器:
  - `src/REMANI-Planner/remani_planner/plan_manage/src/planner_manager.cpp`
  - `src/REMANI-Planner/remani_planner/plan_manage/include/plan_manage/planner_manager.h`
- Optimizer and costs / 优化器与代价函数:
  - `src/REMANI-Planner/remani_planner/traj_opt/include/optimizer/poly_traj_optimizer.hpp`
  - `src/REMANI-Planner/remani_planner/traj_opt/src/poly_traj_optimizer.cpp`
- Trajectory containers / 轨迹容器:
  - `src/REMANI-Planner/remani_planner/traj_utils/include/traj_utils/plan_container.hpp`
- Params / 参数配置:
  - `src/REMANI-Planner/remani_planner/plan_manage/config/mm_param.yaml`
  - `src/REMANI-Planner/remani_planner/plan_manage/config/remani_planner_param.yaml`

## 5) Proposed Phase-1 Implementation Plan / 第一阶段实施计划
### Milestone M1 (Scaffold + Safe Fallback) / 脚手架 + 安全回退
- Add ROS service interface for diffusion arm planner.  
  增加 diffusion 机械臂规划的 ROS service 接口。
- Add a Python `diffusion_arm_planner` service node (dummy first).  
  增加 Python service 节点（先用 dummy 实现）。
- Call service from `planner_manager` in `reboundReplan` path.  
  在 `planner_manager` 的 `reboundReplan` 路径调用服务。
- If service fails or times out, fallback automatically.  
  服务失败/超时自动回退。

### Milestone M2 (Real Diffusion Inference) / 接入真实模型推理
- Replace dummy with mpd model inference.  
  用 mpd 模型推理替换 dummy。
- Input: base time-series, start/goal arm state, optional seed.  
  输入: 底盘时序、机械臂起终点状态、可选 seed。
- Output: arm trajectory prior.  
  输出: 机械臂轨迹先验。
- Keep strict timeout and fallback.  
  保持严格超时和回退机制。

### Milestone M3 (Evaluation and Feedback Loop) / 评估与反馈闭环
- Log diffusion success rate, fallback count, planning time, collision metrics.  
  记录 diffusion 成功率、回退次数、规划时延、碰撞指标。
- If repeated arm failures occur, trigger base replan and retry.  
  机械臂连续失败则触发底盘重规划并重试。
- Compare against baseline traditional-only pipeline.  
  与传统 pipeline 做基线对比。

## 6) Pending Tasks (Next Execution Queue) / 待办队列（下一步）
M1 scaffold is complete and smoke-tested (build + ROS service call + fallback-ready wiring).  
M1 脚手架已完成并通过冒烟验证（编译 + ROS 服务调用 + 回退链路接入）。

1. Replace dummy node logic with MPD inference backend.  
   将 dummy 节点替换为 MPD 推理后端。
2. Define training/inference feature contract (map features, base trajectory encoding, arm state normalization).  
   明确训练/推理特征协议（地图特征、底盘轨迹编码、机械臂状态归一化）。
3. Add failure-feedback hook in FSM to trigger base replan after repeated arm-prior failures.  
   在 FSM 中加入失败反馈钩子，机械臂先验连续失败后触发底盘重规划。
4. Add evaluation script and logs for success rate, latency, collision cost, and fallback ratio.  
   增加评估脚本与日志，统计成功率、时延、碰撞代价与回退比例。
5. Run full simulation regression with and without diffusion arm prior enabled.  
   在仿真中分别开启/关闭 diffusion arm prior，执行回归对比测试。

## 7) Risks and Notes / 风险与备注
- Current `mpd-public` README marks this repo as deprecated, with newer code in `mpd-splines-public`.  
  当前 `mpd-public` README 标注该仓库已 deprecated，官方建议迁移到 `mpd-splines-public`。
- `src/mpd-public` extracted from zip has no git history in that folder.  
  `src/mpd-public` 来自 zip，当前目录不含 git 历史。
- `src/mpd-public/deps/*` currently appear empty and may require explicit setup.  
  `deps` 目录目前为空，可能需要单独补齐依赖。
- Keep phase-1 scope narrow to avoid destabilizing runtime planner behavior.  
  第一阶段要控制范围，避免影响现有在线规划稳定性。

## 8) Daily Log Template / 每日记录模板
Copy this block for each work day.  
每天可复制以下模板填写。

Date / 日期: YYYY-MM-DD  
Focus / 重点:  
Done / 完成:  
Blocked / 阻塞:  
Decisions / 决策:  
Files Changed / 文件改动:  
Next / 下一步:

## 9) Daily Log / 每日记录
Date / 日期: 2026-04-01

Focus / 重点:
- Consolidate workspace and prepare integration plan.  
  整理工作空间并确认集成方案。

Done / 完成:
- Built unified workspace at `/home/yifu/remani_ws/remani_mpd_ws`.  
  建立统一工作空间。
- Ensured both repos are available under `src/`.  
  确认两个项目都在 `src/` 下。
- Cleaned naming and link confusion (`remain_mpd_ws` removed).  
  清理命名与软链接混乱问题。
- Confirmed REMANI integration touchpoints and call chain.  
  确认 REMANI 关键接入点与调用链。
- Finalized architecture decision (traditional base + diffusion arm + fallback).  
  最终确认分层架构方案。
- Implemented `remani_diffusion_msgs` and `diffusion_arm_planner` packages.  
  已实现 `remani_diffusion_msgs` 与 `diffusion_arm_planner` 两个新包。
- Wired diffusion service client into `MMPlannerManager` with automatic fallback path.  
  已在 `MMPlannerManager` 接入 diffusion 服务客户端并打通自动回退。
- Added diffusion config entries and launch-time switches (including direct param override in launch).  
  已补充 diffusion 配置项与 launch 开关（含 launch 直连参数覆盖）。
- Build verified: `catkin_make --pkg remani_diffusion_msgs diffusion_arm_planner remani_planner -DCMAKE_BUILD_TYPE=Release` passed.  
  编译验证通过：`catkin_make --pkg remani_diffusion_msgs diffusion_arm_planner remani_planner -DCMAKE_BUILD_TYPE=Release`。
- ROS smoke test passed for service availability and call behavior.  
  ROS 冒烟测试通过，服务注册与调用行为正常。
- Added request-shape validation in dummy node (`invalid_base_traj` on mismatch).  
  已在 dummy 节点新增请求维度校验（不匹配返回 `invalid_base_traj`）。
- MPD inference pipeline is now runnable in this workspace for 2D model on CPU (official script path).  
  当前工作区已可运行 MPD 官方推理脚本（2D 模型、CPU 模式）。
- Verified inference command (CPU, no render):  
  已验证推理命令（CPU、无渲染）：
  `cd src/mpd-public/scripts/inference && python inference.py --model_id EnvSimple2D-RobotPointMass --device cpu --render false --n_samples 8`
- Runtime env vars used in this environment: `MPLCONFIGDIR=/tmp/mplconfig`, `XDG_CACHE_HOME=/tmp/xdg-cache`, `TORCH_EXTENSIONS_DIR=/tmp/torch_extensions`, `MPD_RESULTS_DIR=src/mpd-public/results_inference_local`.  
  当前环境建议设置运行变量：`MPLCONFIGDIR=/tmp/mplconfig`、`XDG_CACHE_HOME=/tmp/xdg-cache`、`TORCH_EXTENSIONS_DIR=/tmp/torch_extensions`、`MPD_RESULTS_DIR=src/mpd-public/results_inference_local`。
- Verified output artifact:  
  已验证输出文件：
  `src/mpd-public/results_inference_local/EnvSimple2D-RobotPointMass/30/results_data_dict.pickle`
- Metrics from successful run (sample): success=1, free-traj ratio=0.375, t_total≈0.352s.  
  成功运行样例指标：success=1，free-traj 比例=0.375，t_total≈0.352s。

Blocked / 阻塞:
- Panda/IsaacGym 3D inference in this environment is still constrained by GPU/CUDA access and IsaacGym runtime requirements.  
  当前环境下 Panda/IsaacGym 的 3D 推理仍受 GPU/CUDA 访问和 IsaacGym 运行时限制。

Decisions / 决策:
- Start with arm-only diffusion prior integration (phase-1).  
  第一阶段先做 arm-only diffusion 先验接入。

Files Changed / 文件改动:
- Created/updated this file: `PROJECT_PROGRESS.md`  
  创建/更新本文件。

Next / 下一步:
- Start M2: replace dummy logic with real MPD diffusion inference path.  
  进入 M2：将 dummy 逻辑替换为真实 MPD diffusion 推理链路。
