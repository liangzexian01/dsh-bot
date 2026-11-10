---
name: memory-continuity
description: 跨会话/跨 Bot 记忆语义连贯召回协议（贾维斯基座 6.4.4）：把 muse 语义索引 + 本线结构化状态 + shared-memory 跨对话入口三层编排成连贯上下文包。只读索引，零新建存储。
---

# memory-continuity：跨会话/跨 Bot 记忆语义连贯召回协议

> 来源：贾维斯基座 6.4.4（2026-11-10），实证见 `dsh-bot-evolution/贾维斯基座6.4/6.4.4-跨会话记忆语义连贯方案.md`
> 用途：让 bot 跨会话/跨 Bot 拿到连贯上下文，不新建存储、只读已有索引

## 目标
把三处已有的记忆后端编排成一个"连贯上下文包"召回协议，解决"换会话/换 Bot 就失忆"的问题。不新建存储，只串已有后端：muse 语义索引 + 本线结构化状态 + shared-memory 跨对话入口。

## 前置条件
- `~/.dsh/muse/index.json` 语义索引存在（muse skill 维护，可读不可改）。
- 本线结构化状态锚点文件（如 `dsh-bot-evolution/贾维斯基座_状态.json`）存在。
- `~/.dsh/shared-memory/index.json` 倒排 n-gram→memoryId 跨对话入口存在（shared-memory skill 维护，只读）。
- 不碰 `muse/state.json`（属 muse skill）、`assistants/`、`ego/`、`state.json`（只读索引）。

## 步骤
1. **语义层召回**：查 `~/.dsh/muse/index.json`（关键词+标签+实体加权）拿相关条目。
2. **结构化状态层召回**：读本线状态 JSON，按当前阶段/任务查进度与开放项。
3. **跨对话入口层召回**：查 `~/.dsh/shared-memory/index.json`，用 n-gram 命中 memoryId，跨 Bot/跨会话取回上下文。
4. **编排成包**：三层结果合成连贯上下文包，作为本次任务背景。
5. **增强不替代**：召回内容用于上下文增强，不替代用户明确指令；涉及授权/凭据仍走 autonomy-policy。

## 常见坑
- 把 `shared-memory/sessions.json` 当记忆内容：它只是会话统计，真实语义内容在 `muse/index.json` 与 `shared-memory/index.json`。
- 往 `muse/index.json` 手写写入：只读索引，由 muse skill 维护，别手改。
- 把本线状态写进 `muse/state.json`：本线结构化状态放自己的 JSON 锚点，不碰 muse 的。
- 召回 ≠ 指令：增强上下文，最终以用户明确指令为准。

## 验收标准
- [ ] 三层各能命中（语义/结构化/跨对话）并标记 coherent。
- [ ] PoC 跑通（`memory-continuity-poc.py --demo`）三层均 `coherent=true`。
- [ ] 只读：零新建存储、不改 `muse/state.json`、assistants/ 零改动。
- [ ] 与 1.2 闸门解耦。
