# -*- coding: utf-8 -*-
"""生成大肥鱼桌宠的全套“QQ弹弹”风格音效（16-bit mono WAV）。"""
import math
import os
import random
import struct
import wave

SR = 44100
OUT = os.environ.get("SOUND_OUT") or os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
random.seed(20240911)


def save_wav(name, samples):
    path = os.path.join(OUT, name)
    frames = bytearray()
    for s in samples:
        v = int(max(-1.0, min(1.0, s)) * 32767)
        frames += struct.pack("<h", v)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(bytes(frames))
    print("WROTE %-14s %.3fs %d bytes" % (name, len(samples) / SR, os.path.getsize(path)))


def tone(freq, dur, decay=6.0, attack=0.004, volume=1.0, vibrato=0.0, harmonic=0.0):
    n = max(1, int(SR * dur))
    out = []
    for i in range(n):
        t = i / SR
        phase = 2.0 * math.pi * freq * t
        if vibrato:
            phase += vibrato * math.sin(2.0 * math.pi * 6.0 * t)
        s = math.sin(phase) + harmonic * math.sin(2.0 * phase)
        a = min(1.0, t / attack) if attack > 0 else 1.0
        env = a * math.exp(-decay * t / dur)
        out.append(volume * s * env / (1.0 + abs(harmonic)))
    return out


def glide(f0, f1, dur, decay=5.0, attack=0.004, wobble=0.0, harmonic=0.35, volume=1.0):
    n = max(1, int(SR * dur))
    out = []
    if abs(f1 - f0) > 1.0:
        k = math.log(f1 / f0)
        for i in range(n):
            t = i / SR
            phase = 2.0 * math.pi * f0 * dur / k * (math.exp(k * t / dur) - 1.0)
            s = math.sin(phase) + harmonic * math.sin(2.0 * phase)
            if wobble:
                s *= 1.0 + wobble * math.sin(2.0 * math.pi * 18.0 * t)
            a = min(1.0, t / attack) if attack > 0 else 1.0
            env = a * math.exp(-decay * t / dur)
            out.append(volume * s * env / (1.0 + harmonic))
    else:
        return tone(f0, dur, decay, attack, volume, harmonic=harmonic)
    return out


def noise(dur, decay=8.0, attack=0.002, cutoff=0.25, volume=0.8):
    n = max(1, int(SR * dur))
    out = []
    prev = 0.0
    for i in range(n):
        t = i / SR
        white = random.uniform(-1.0, 1.0)
        prev = prev + cutoff * (white - prev)
        a = min(1.0, t / attack) if attack > 0 else 1.0
        env = a * math.exp(-decay * t / dur)
        out.append(volume * prev * env)
    return out


def concat(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return out


def mix(*parts):
    n = max(len(p) for p in parts) if parts else 0
    out = [0.0] * n
    for p in parts:
        for i, s in enumerate(p):
            out[i] += s
    peak = max(1e-9, max(abs(s) for s in out)) if out else 1.0
    if peak > 1.0:
        out = [s / peak for s in out]
    return out


def main():
    # 基础交互
    save_wav("click.wav", glide(880, 420, 0.16, decay=9.0, wobble=0.15))
    save_wav("takeoff.wav", glide(320, 900, 0.28, decay=3.2, wobble=0.12))
    save_wav("landing.wav", glide(520, 180, 0.32, decay=4.0, wobble=0.25))

    # 控制面板
    save_wav("feed.wav", concat(
        mix(noise(0.09, decay=13, cutoff=0.22, volume=0.9), tone(190, 0.09, decay=10, volume=0.5)),
        mix(noise(0.08, decay=13, cutoff=0.22, volume=0.8), tone(160, 0.08, decay=10, volume=0.4)),
    ))
    save_wav("talk.wav", tone(660, 0.10, decay=7.0, vibrato=0.25, volume=0.9))
    save_wav("happy.wav", concat(
        tone(523, 0.11, decay=5.0, volume=0.9),
        tone(659, 0.11, decay=5.0, volume=0.9),
        tone(784, 0.20, decay=4.0, volume=0.95),
    ))
    save_wav("rest.wav", glide(440, 220, 0.50, decay=2.5, volume=0.55))
    save_wav("mode_wander.wav", glide(600, 420, 0.12, decay=9.0, volume=0.7))
    save_wav("mode_follow.wav", glide(720, 520, 0.12, decay=9.0, volume=0.7))
    save_wav("mode_still.wav", glide(500, 320, 0.12, decay=9.0, volume=0.7))
    save_wav("ui_click.wav", tone(1000, 0.055, decay=14.0, volume=0.55))
    save_wav("hide.wav", mix(
        noise(0.26, decay=5.0, cutoff=0.10, volume=0.55),
        glide(620, 160, 0.26, decay=4.0, volume=0.55),
    ))
    save_wav("grumpy.wav", tone(115, 0.32, decay=2.2, volume=0.8, harmonic=0.9, vibrato=0.5))
    save_wav("pop.wav", glide(700, 500, 0.10, decay=10.0, wobble=0.2, volume=0.7))

    print("DONE", OUT)


if __name__ == "__main__":
    main()
