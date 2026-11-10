#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
voice-io-poc.py — 贾维斯基座 6.4.2 语音入口最小闭环 PoC
零安装 TTS（Windows SAPI）+ 离线 STT（Vosk）。无外部账号、无云依赖。

用法：
  python voice-io-poc.py --tts-wav  out.wav "测试语音输出"   # SAPI 念到 wav，不发声
  python voice-io-poc.py --tts-speak "测试语音输出"          # SAPI 直接发声
  python voice-io-poc.py --stt-check                         # 加载模型 + 列出麦克风设备
  python voice-io-poc.py --stt-mic 5                         # 录 5 秒麦克风并转写
  python voice-io-poc.py --loop                              # 说一句->文本->TTS 念回（常驻）
"""
import argparse, os, sys, tempfile, urllib.request, zipfile, shutil

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip"
# 注意：Vosk 的 C++ 层用窄字符(ANSI)路径，无法从含非 ASCII 用户名(如 梁泽贤)的路径加载模型，
# 必须用纯 ASCII 绝对路径。下载的 zip 仍保留在脚本同目录作为产物。
MODEL_DIR = r"C:\vosk-model-small-cn-0.22"

def ensure_model():
    if os.path.isdir(MODEL_DIR):
        return MODEL_DIR
    print(f"[模型] 本地无模型，从公开 CDN 一次性下载（无账号）：{MODEL_URL}")
    zip_path = MODEL_DIR + ".zip"
    urllib.request.urlretrieve(MODEL_URL, zip_path)
    print("[模型] 下载完成，解压中…")
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(os.path.dirname(MODEL_DIR))
    os.remove(zip_path)
    print(f"[模型] 就绪：{MODEL_DIR}")
    return MODEL_DIR

def tts_powershell(text, wav_path=None):
    """用 Windows SAPI 发音；wav_path 给定则写文件不发声。零 pip 依赖。"""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False)
    tmp.write(text); tmp.close()
    if wav_path:
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.SetOutputToWaveFile('{wav_path}'); "
            f"$s.Speak([System.IO.File]::ReadAllText('{tmp.name}',[System.Text.Encoding]::UTF8)); "
            "$s.Dispose()"
        )
    else:
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.Speak([System.IO.File]::ReadAllText('{tmp.name}',[System.Text.Encoding]::UTF8)); "
            "$s.Dispose()"
        )
    os.system(f'powershell -NoProfile -Command "{ps}"')
    os.unlink(tmp.name)
    if wav_path:
        print(f"[TTS] 已写入 WAV：{wav_path}（{os.path.getsize(wav_path)} bytes）")

def stt_check():
    try:
        import vosk, sounddevice
    except ImportError as e:
        print(f"[STT] 缺少依赖，请先：pip install vosk sounddevice （{e}）")
        return
    md = ensure_model()
    print(f"[STT] 模型加载：{md}")
    import sounddevice as sd
    print("[STT] 输入设备列表：")
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0:
            print(f"  [{i}] {d['name']} (in={d['max_input_channels']})")
    print("[STT] 引擎与设备就绪，运行 --stt-mic N 做实时听写。")

def stt_mic(seconds):
    try:
        import vosk, sounddevice, queue
    except ImportError as e:
        print(f"[STT] 缺少依赖，请先：pip install vosk sounddevice （{e}）")
        return
    import json, sys
    from vosk import Model, KaldiRecognizer
    md = ensure_model()
    model = Model(MODEL_DIR)
    rec = KaldiRecognizer(model, 16000)
    q = queue.Queue()
    def cb(indata, frames, t, status):
        q.put(bytes(indata))
    import sounddevice as sd
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=cb):
        print(f"[STT] 录音 {seconds}s，请说话…")
        text_parts = []
        import time
        end = time.time() + seconds
        while time.time() < end:
            data = q.get()
            if rec.AcceptWaveform(data):
                r = json.loads(rec.Result())
                if r.get("text"):
                    text_parts.append(r["text"])
            else:
                p = json.loads(rec.PartialResult())
                if p.get("partial"):
                    sys.stdout.write("\r[STT] … " + p["partial"]); sys.stdout.flush()
        final = json.loads(rec.FinalResult())
        if final.get("text"):
            text_parts.append(final["text"])
        full = " ".join(text_parts).strip()
        print(f"\n[STT] 识别结果：{full}")
        return full

def loop():
    print("[LOOP] 说一句->转写->TTS 念回（Ctrl+C 退出）")
    while True:
        try:
            text = stt_mic(5)
            if text:
                tts_powershell("收到：" + text)
        except KeyboardInterrupt:
            print("\n[LOOP] 退出"); break

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tts-wav", nargs=2, metavar=("WAV", "TEXT"))
    ap.add_argument("--tts-speak", metavar="TEXT")
    ap.add_argument("--stt-check", action="store_true")
    ap.add_argument("--stt-mic", type=int, metavar="SECONDS")
    ap.add_argument("--loop", action="store_true")
    args = ap.parse_args()

    if args.tts_wav:
        tts_powershell(args.tts_wav[1], wav_path=args.tts_wav[0])
    elif args.tts_speak:
        tts_powershell(args.tts_speak)
    elif args.stt_check:
        stt_check()
    elif args.stt_mic is not None:
        stt_mic(args.stt_mic)
    elif args.loop:
        loop()
    else:
        ap.print_help()
