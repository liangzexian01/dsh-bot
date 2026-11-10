# autonomy-policy（自治策略层 skill）

> 来源：贾维斯基座 6.4.3（2026-11-10）
> 用途：任务入口先判"自主干 vs 请示"，留决策日志，安全侧默认请示
> LICENSE：Apache 2.0

## 结构

```
autonomy-policy/
├── SKILL.md   # 五段结构（目标/前置/步骤/常见坑/验收）
├── README.md  # 本文件
└── LICENSE    # Apache 2.0
```

## 注册为共享能力

已通过 `save_capability(name="autonomy-policy", kind="skill", description=原值, content=五段正文)` 注册为 DSH 共享 skill（系统返回 `Saved autonomy-policy.`）。其他 Bot 用前先 `attach_capability("autonomy-policy")`，再 `skill("autonomy-policy")` 读正文，用完 `detach_capability("autonomy-policy")` 摘回。

## 详细方案与实证

沉淀来源与实证见仓库内 `dsh-bot-evolution/贾维斯基座6.4/6.4.3-自治策略层方案.md`、`dsh-bot-evolution/贾维斯基座6.4/autonomy-policy-poc.py`、`dsh-bot-evolution/贾维斯基座6.4/autonomy-decision-log.md`。
