#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory-continuity-poc.py — 6.4.4 跨会话记忆语义连贯 MVP 召回编排器

把三层记忆后端编排成连贯「上下文包（context pack）」，证明跨会话/跨 Bot
语义连贯召回可运行。只读索引，零新建存储、零越界：

  1) 语义层  ：(~/.dsh/muse/index.json)                muse-core 内容理解语义索引
  2) 结构化状态层：(本线 dsh-bot-evolution/贾维斯基座_状态.json)  6.4 进度锚点
  3) 跨对话入口层：(~/.dsh/shared-memory/index.json)   shared-memory 倒排 n-gram→memoryId

用法：
  python memory-continuity-poc.py --demo        # 内置三词验证（绕过 GBK 参数截断）
  python memory-continuity-poc.py "贾维斯"       # 直接查询
"""
import argparse
import io
import json
import os
import re
import sys
import datetime

# 强制 stdout/stderr 走 utf-8，避免 GBK 控制台报 UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

WORK = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
MUSE_INDEX = os.path.join(HOME, ".dsh", "muse", "index.json")
STATE_FILE = os.path.join(WORK, "贾维斯基座_状态.json")
SHARED_INDEX = os.path.join(HOME, ".dsh", "shared-memory", "index.json")


def load_json(p):
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_error": str(e)}


def recall_semantic(query, items):
    """语义层：在 muse 条目的 summary/tags/entities/topics/text 做子串匹配。"""
    q = query.lower().strip()
    toks = [t for t in re.split(r"\s+", q) if t]
    hits = []
    for it in (items or []):
        if not isinstance(it, dict):
            continue
        hay = " ".join([
            it.get("summary", ""),
            " ".join(it.get("tags", [])),
            " ".join(it.get("entities", [])),
            " ".join(it.get("topics", [])),
            it.get("text", ""),
        ]).lower()
        if q in hay or any(t in hay for t in toks):
            hits.append(it)
    return hits


def recall_state(query, state):
    """结构化状态层：返回 steps 中含查询词的进度项。"""
    out = {}
    if not isinstance(state, dict):
        return out
    for k, v in (state.get("steps") or {}).items():
        if query.lower() in (k + str(v)).lower():
            out[k] = v
    return out


def recall_shared(query, inv):
    """跨对话入口层：在 shared-memory 倒排索引里匹配 n-gram 键，返回去重 memoryId。"""
    if not isinstance(inv, dict):
        return [], []
    q = query.strip()
    matched_keys = []
    ids = []
    for key, vals in inv.items():
        if q in key or (len(q) >= 2 and key in q):  # n-gram 重叠
            matched_keys.append(key)
            for vid in (vals or []):
                if vid not in ids:
                    ids.append(vid)
    return matched_keys, ids


def run(query, bot="进化规划师"):
    muse = load_json(MUSE_INDEX)
    if isinstance(muse, dict) and "_error" in muse:
        muse = []
    state = load_json(STATE_FILE) or {}
    if isinstance(state, dict) and "_error" in state:
        state = {}
    shared = load_json(SHARED_INDEX)
    if isinstance(shared, dict) and "_error" in shared:
        shared = {}

    print(f"[MEMORY-CONTINUITY] query={query}  bot={bot}  "
          f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}")

    sem = recall_semantic(query, muse)
    st = recall_state(query, state)
    keys, ids = recall_shared(query, shared)

    print(f"-- 1) 语义层(muse/index.json) 命中 {len(sem)} 条 --")
    for it in sem:
        print(f"  - [{it.get('kind')}] {it.get('summary','')[:90]}")

    print(f"-- 2) 结构化状态层(贾维斯基座_状态.json) 命中 {len(st)} 项 --")
    for k, v in st.items():
        print(f"  - {k}: {v}")

    print(f"-- 3) 跨对话入口层(shared-memory/index.json) 命中键 {len(keys)} "
          f"个 / memoryId {len(ids)} 个 --")
    for k in keys[:8]:
        print(f"  - ngram[{k}]")
    if ids:
        print(f"  -> memoryIds: {', '.join(ids[:8])}")

    pack = {
        "query": query,
        "bot": bot,
        "semantic_hits": [it.get("summary", "") for it in sem],
        "state_hits": st,
        "shared_memory_ids": ids,
        "coherent": bool(sem or st or ids),
    }
    print("-- context pack（连贯上下文）--")
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return pack


def main():
    ap = argparse.ArgumentParser(description="6.4.4 跨会话记忆语义连贯召回编排器")
    ap.add_argument("query", nargs="?", help="召回查询词")
    ap.add_argument("--query", dest="q2", help="召回查询词(同位置参数)")
    ap.add_argument("--bot", default="进化规划师", help="执行 bot 名")
    ap.add_argument("--demo", action="store_true",
                    help="内置三词验证（贾维斯/自我提升/6.4），绕过 GBK 参数截断")
    args = ap.parse_args()

    if args.demo:
        # 三词各命中一层：语义层 / 结构化状态层 / 跨 Bot 入口层
        # （注：shared-memory 中本项目的键以 ASCII "jarvis" 存储，故用 jarvis 触发第三层）
        for q in ["自我提升", "6.4", "jarvis"]:
            run(q, args.bot)
            print("=" * 60)
        return

    q = args.query or args.q2 or "贾维斯"
    run(q, args.bot)


if __name__ == "__main__":
    main()
