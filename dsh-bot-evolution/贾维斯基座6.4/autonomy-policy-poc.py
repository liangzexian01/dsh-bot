#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
autonomy-policy-poc.py — 6.4.3 自治策略层 MVP 判定器
给定任务文本，按判定矩阵输出 自主(AUTONOMY) / 请示(ASK) + 触发规则 + 原因，
并写入决策日志 dsh-bot-evolution/autonomy-decision-log.md。

设计原则：安全侧默认——先扫 ASK 规则，命中即请示；再扫 AUTO 规则，命中即自主；
两者都不中 → 默认请示（ASK）。绝不因"自治"而擅动高危/越界动作。

用法：
  python autonomy-policy-poc.py "截个屏看看现在在干嘛"
  python autonomy-policy-poc.py --task "帮我把 state.json 改一下"
  python autonomy-policy-poc.py --dry-run "查一下本机内存占用"
"""
import argparse
import re
import os
import json
import datetime

# ---- 判定矩阵 ----
# 请示规则（高优先，命中即停）：涉及授权/凭据/不可逆/越界/外部/高危/常驻/未验证
ASK_RULES = [
    (r"外部账号|登录|登入|登出|退出登录|注册|开通", "涉及外部账号/身份"),
    (r"凭据|token|密码|密钥|secret|api[_ ]?key|pat", "涉及凭据/密钥"),
    (r"支付|付款|购买|订阅|付费|花钱|转账|充值|扣费", "涉及金钱支付"),
    (r"删除|清空|格式化|rm\s|del\s|drop\s|永久移除", "不可逆删除动作"),
    (r"强关|强制关闭|kill|结束进程|终止进程", "强制结束进程/窗口"),
    (r"发邮件|发消息|发短信|外发|推送|发布|上传|提交\s*github|commit\s*push|推送到|发推|发帖", "对外发送/发布动作"),
    (r"(改|写|删|动).{0,4}(assistants|ego|state\.json)|(assistants|ego|state\.json).{0,4}(改|写|删|动)|改用户画像", "越界写受保护目录(闸门未过)"),
    (r"ssh|远程|rdp|vpn|内网|渗透|攻击|扫描端口|爆破", "远程/网络攻击类动作"),
    (r"常驻|监听|实时盯|后台轮询|7x24", "常驻监听/高成本常驻"),
    (r"授权|批准我|允许我|替我|代我操作", "需用户明确授权"),
    (r"下载模型|装包|pip\s*install|安装软件|运行未知|执行未知", "安装/运行未验证程序"),
]

# 自主规则（仅当明确命中且不涉及上述 ASK 时）
AUTO_RULES = [
    (r"截.{0,3}(屏|图)|截图|看屏幕|看一眼|屏幕在干嘛|列窗口|当前窗口|前台程序", "本机只读-桌面感知(desktop-control 已验证)"),
    (r"读此?机|本机状态|内存|cpu|磁盘|进程列表|系统信息", "本机只读-状态查询"),
    (r"写\s*方案|写\s*规划|写\s*日志|写文档|记一下|落盘|总结|整理|生成报告", "本线 dsh-bot-evolution/ 规划文档(可写)"),
    (r"检索|查找 skill|find-?skill|搜一下|查资料|读记忆|回忆|读\s*memory", "检索/记忆读取(find-skill/memory 已验证)"),
    (r"语音|念回|听写|stt|tts|说话", "本地语音 I/O(voice-io 已验证范围)"),
    (r"打开(公开)?网页|访问(公开)?网站|读(公开)?网页", "公开网页读取(ego 已验证范围,不含登录态复用)"),
]


def classify(task: str):
    for pat, reason in ASK_RULES:
        if re.search(pat, task, re.IGNORECASE):
            return ("ASK", reason, f"ASK:{pat}")
    for pat, reason in AUTO_RULES:
        if re.search(pat, task, re.IGNORECASE):
            return ("AUTONOMY", reason, f"AUTO:{pat}")
    return ("ASK", "未命中任何明确自主规则，按安全侧默认请示", "DEFAULT:ASK")


def main():
    ap = argparse.ArgumentParser(description="6.4.3 自治策略层 MVP 判定器")
    ap.add_argument("task", nargs="?", help="任务描述文本")
    ap.add_argument("--task", dest="task_opt", help="任务描述(同位置参数)")
    ap.add_argument("--dry-run", action="store_true", help="只判定不写日志")
    ap.add_argument("--bot", default="进化规划师", help="执行 bot 名")
    args = ap.parse_args()
    task = args.task or args.task_opt
    if not task:
        ap.error("必须提供任务描述")

    verdict, reason, rule = classify(task)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rec = {
        "timestamp": ts,
        "bot": args.bot,
        "task": task,
        "verdict": verdict,
        "reason": reason,
        "rule": rule,
        "user_confirmed": None if verdict == "AUTONOMY" else "pending",
    }

    print(f"[AUTONOMY-POLICY] {ts}")
    print(f"  bot      : {args.bot}")
    print(f"  task     : {task}")
    print(f"  verdict  : {verdict}  ({'自主执行' if verdict == 'AUTONOMY' else '先请示用户'})")
    print(f"  reason   : {reason}")
    print(f"  rule     : {rule}")
    if verdict == "ASK":
        print("  >> 停下，向用户呈报，等明确点头再执行。")
    else:
        print("  >> 在已验证能力范围内自主执行，并留日志。")

    if not args.dry_run:
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "autonomy-decision-log.md")
        line = (f"| {ts} | {args.bot} | {verdict} | {reason} | {rule} | {task} | "
                f"{rec['user_confirmed']} |\n")
        header = ("# 自治决策日志（6.4.3 MVP）\n\n"
                  "| 时间 | Bot | 判定 | 触发原因 | 规则 | 任务 | 用户确认 |\n"
                  "| --- | --- | --- | --- | --- | --- | --- |\n")
        if not os.path.exists(log_path):
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(header)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
        print(f"  log      : appended -> {log_path}")

    print(json.dumps(rec, ensure_ascii=False))


if __name__ == "__main__":
    main()
