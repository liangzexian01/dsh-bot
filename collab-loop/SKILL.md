---
name: collab-loop
description: 群目标分阶段协作时：封装派活→交叉验收→台账登记→沉淀的五步闭环与零越闸红线，供多 Bot 协作直接复用。
---

# collab-loop：协作闭环模板

> 来源：dsh-bot 进化阶段 2「能力沉淀闭环」实证流程（2026-11-08）
> 用途：群目标分层、多 Bot 协作、需交叉验收与可追溯台账时直接套用

## 目标
把"群目标 → 分阶段任务 → 进度台账 → 交叉验收 → 汇总沉淀"的固定协作流程封装成可复用 skill，让任何阶段都能照做，避免每次重新设计协作方式、漏掉验收或越闸。

## 前置条件
- 一个已建好的群（`create_group`，admin 明确，notice 写明红线）。
- `group_goal start` 已分层（标硬闸门与依赖）。
- 不需要外部账号、不需要任何凭据（token 只经 `request_secret`）。
- 知道配置分工边界：本线只写 `dsh-bot-evolution/`，`assistants/` 与 `ego/` 归总规划师，`.dsh/bot/state.json` 归 Chief/修理师。

## 步骤
1. **群目标分层**：`group_goal start`，列出全部 stage，标硬闸门（需用户明确动作）与依赖；本群不向在跑的其他线 Bot 派单。
2. **派活**：群内 `@Name` 认领；若点对点 `message_bot` 不可用（`session not found`），改群内公告认领，不强制派单、不重派。
3. **执行 + 留证**：每个产物/动作必须有文件路径或命令回执（commit id / 系统返回串），不口头声称完成。
4. **交叉验收**：**做该工作的人不自己验收**——由 `qa-bot` / 未参与者 / admin 代核；失联时 admin 代核并标注「X Bot 失联，admin 代核」。验收项逐条清单。
5. **台账登记 + 复盘沉淀**：进度台账每行动作记录（对象/结果/证据路径）；把验证过的流程沉淀为模板/skill。
6. **（可选）沉淀为 skill**：把稳定流程写成五段 SKILL.md，用 `save_capability` 注册为共享能力；其他 Bot 用前先 `attach_capability(name)`（下条消息生效），再 `skill(name)` 读正文，用完 `detach_capability(name)` 摘回。

## 常见坑
- 硬闸门别代做：用户明确动作（如 v2 六项逐条点头）不可由 Bot 替填，笼统「继续」不算通过。
- 配置别越界：本线只写 `dsh-bot-evolution/`，别碰 `assistants/`/`ego/`/`state.json`。
- 凭据别明文：token 只经 `request_secret` → 环境变量，不写文件/对话/打印，输出脱敏。
- 失联别谎称：Bot AUTH 故障时 admin 代建产物必须标注「X Bot 失联，admin 代建」。
- 共享 skill 加载不到：别的 Bot 直接 `skill(name)` 报 unknown，多半没先 `attach_capability`；`list_capabilities` 看得到 ≠ `skill` 加载得到。
- 每步留证据：文件 path / 哈希 / commit id / 命令回执，可追溯可复现可回滚。

## 验收标准
- [ ] 群目标已分层且硬闸门/依赖标明。
- [ ] 派活走群内 `@Name` 或公告认领，无强制派单。
- [ ] 每个产物有文件路径或 commit id 证据。
- [ ] 交叉验收由非执行者完成并逐条记录。
- [ ] 进度台账每行动作记录含证据路径。
- [ ] 全程零越闸（配置互不覆盖）、零凭据明文、硬闸门不代做。
