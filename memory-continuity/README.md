# memory-continuity（跨会话/跨 Bot 记忆语义连贯召回协议 skill）

> 来源：贾维斯基座 6.4.4（2026-11-10）
> 用途：把 muse 语义索引 + 本线结构化状态 + shared-memory 跨对话入口编排成连贯上下文包；只读、零新建存储
> LICENSE：Apache 2.0

## 结构

```
memory-continuity/
├── SKILL.md   # 五段结构（目标/前置/步骤/常见坑/验收）
├── README.md  # 本文件
└── LICENSE    # Apache 2.0
```

## 注册为共享能力

已通过 `save_capability(name="memory-continuity", kind="skill", description=原值, content=五段正文)` 注册为 DSH 共享 skill（系统返回 `Saved memory-continuity.`）。其他 Bot 用前先 `attach_capability("memory-continuity")`，再 `skill("memory-continuity")` 读正文，用完 `detach_capability("memory-continuity")` 摘回。

## 详细方案与实证

沉淀来源与实证见仓库内 `dsh-bot-evolution/贾维斯基座6.4/6.4.4-跨会话记忆语义连贯方案.md`、`dsh-bot-evolution/贾维斯基座6.4/memory-continuity-poc.py`、`dsh-bot-evolution/贾维斯基座6.4/贾维斯基座_状态.json`。
