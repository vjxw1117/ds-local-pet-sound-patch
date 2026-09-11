# -*- coding: utf-8 -*-
"""Short WAV sound effects for the desktop pet.

Prefers Qt Multimedia's ``QSoundEffect`` (overlapping playback + per-sound
volume); falls back to ``winsound`` on Windows.  Missing files are ignored so
a partial sound pack never crashes the pet.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from PySide6.QtCore import QUrl
    from PySide6.QtMultimedia import QSoundEffect
except Exception:  # pragma: no cover - Qt Multimedia missing
    QSoundEffect = None
    QUrl = None

try:  # Windows-only, part of the standard library
    import winsound
except Exception:  # pragma: no cover - non-Windows
    winsound = None


SOUND_NAMES = (
    "click", "takeoff", "landing", "feed", "talk", "happy", "rest",
    "mode_wander", "mode_follow", "mode_still", "ui_click", "hide",
    "grumpy", "pop",
)

# Relative emphasis per sound (0.0..1.0); the base volume scales these.
VOLUMES = {
    "click": 0.75,
    "ui_click": 0.65,
    "pop": 0.75,
    "takeoff": 0.90,
    "landing": 0.90,
    "mode_wander": 0.75,
    "mode_follow": 0.75,
    "mode_still": 0.75,
    "talk": 0.90,
    "feed": 0.90,
    "happy": 1.00,
    "rest": 0.80,
    "hide": 0.80,
    "grumpy": 1.00,
}


class SoundPlayer:
    """Play short WAV effects without blocking the Qt event loop."""

    def __init__(
        self,
        sound_dir: str | os.PathLike[str],
        *,
        volume: float = 0.60,
        enabled: bool = True,
    ) -> None:
        self.sound_dir = Path(sound_dir)
        self.volume = max(0.0, min(1.0, float(volume)))
        self.enabled = bool(enabled)
        self._effects: dict[str, object] = {}
        self._winsound_paths: dict[str, str] = {}

        if QSoundEffect is not None and QUrl is not None:
            for name in SOUND_NAMES:
                path = self.path_for(name)
                if not path.is_file():
                    continue
                try:
                    effect = QSoundEffect()
                    effect.setSource(QUrl.fromLocalFile(str(path)))
                    effect.setVolume(self._volume_for(name))
                    effect.setLoopCount(1)
                    self._effects[name] = effect
                except Exception:
                    continue
        elif winsound is not None:
            for name in SOUND_NAMES:
                path = self.path_for(name)
                if path.is_file():
                    self._winsound_paths[name] = str(path)

    # -- public API ---------------------------------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def _volume_for(self, name: str) -> float:
        return max(0.0, min(1.0, self.volume * VOLUMES.get(name, 0.8)))

    def path_for(self, name: str) -> Path:
        filename = name if name.lower().endswith(".wav") else f"{name}.wav"
        return self.sound_dir / filename

    def play(self, name: str) -> bool:
        if not self.enabled:
            return False
        key = name[:-4] if name.lower().endswith(".wav") else name

        effect = self._effects.get(key)
        if effect is not None:
            try:
                effect.play()  # type: ignore[attr-defined]
                return True
            except Exception:
                pass

        if winsound is not None:
            path = self._winsound_paths.get(key) or str(self.path_for(key))
            if os.path.isfile(path):
                try:
                    winsound.PlaySound(
                        path,
                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT,
                    )
                    return True
                except Exception:
                    return False
        return False
