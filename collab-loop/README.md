# collab-loop（协作闭环模板 skill）

> 来源：dsh-bot 进化阶段 2「能力沉淀闭环」实证流程（2026-11-08）
> 用途：群目标分层、多 Bot 协作、需交叉验收与可追溯台账时直接套用
> LICENSE：Apache 2.0

## 结构

```
collab-loop/
├── SKILL.md   # 五段结构 + 零越闸红线（目标/前置/步骤/常见坑/验收）
├── README.md  # 本文件
└── LICENSE    # Apache 2.0
```

## 注册为共享能力

已通过 `save_capability(name="collab-loop", kind="skill", description=原值, content=五段正文)` 注册为 DSH 共享 skill（系统返回 `Saved collab-loop.`）。其他 Bot 用前先 `attach_capability("collab-loop")`（下一条消息生效、catalog 刷新），再 `skill("collab-loop")` 读正文，用完 `detach_capability("collab-loop")` 摘回原状。

## 详细模板与实证

沉淀来源与实证记录见 `dsh-bot-evolution/协作闭环模板.md`（同仓库路径 `dsh-bot-evolution/collab-loop/` 的上级目录）。
