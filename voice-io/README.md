# voice-io（本地/离线语音入口 skill）

> 来源：贾维斯基座 6.4.2（2026-11-10）
> 用途：执行 bot 的听（STT）/说（TTS）能力，零外部账号、离线可用
> LICENSE：Apache 2.0

## 结构

```
voice-io/
├── SKILL.md   # 五段结构（目标/前置/步骤/常见坑/验收）
├── README.md  # 本文件
└── LICENSE    # Apache 2.0
```

## 注册为共享能力

已通过 `save_capability(name="voice-io", kind="skill", description=原值, content=五段正文)` 注册为 DSH 共享 skill（系统返回 `Saved voice-io.`）。其他 Bot 用前先 `attach_capability("voice-io")`（下一条消息生效、catalog 刷新），再 `skill("voice-io")` 读正文，用完 `detach_capability("voice-io")` 摘回原状。

## 详细方案与实证

沉淀来源与实证见仓库内 `dsh-bot-evolution/贾维斯基座6.4/6.4.2-语音入口方案.md`、`dsh-bot-evolution/贾维斯基座6.4/voice-io-poc.py`。
