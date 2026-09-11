# -*- coding: utf-8 -*-
"""Inject pet sound-effect calls into pet/window.py (idempotent)."""
import os

# Run this script from the root of a QCYTSN/ds-local-pet checkout.
ROOT = os.path.dirname(os.path.abspath(__file__))
WINDOW = os.path.join(ROOT, "pet", "window.py")

with open(WINDOW, "r", encoding="utf-8") as f:
    text = f.read()

PATCHES = []


def patch(old, new, label):
    global text
    if old not in text:
        PATCHES.append(("MISSING", label))
        return
    if new in text:
        PATCHES.append(("ALREADY", label))
        return
    text = text.replace(old, new, 1)
    PATCHES.append(("OK", label))


# 1) imports
patch(
    "    QApplication,\n",
    "    QAbstractButton,\n    QApplication,\n",
    "import QAbstractButton",
)
patch(
    "from settings.panel import PetControlPanel\n",
    "from settings.panel import PetControlPanel\nfrom sound import SoundPlayer\n",
    "import SoundPlayer",
)

# 2) create the player
patch(
    "        self.bubble = Bubble()\n",
    '        self.bubble = Bubble()\n        self.sound = SoundPlayer(self.paths.bundle_dir / "sounds")\n',
    "create SoundPlayer",
)

# 3) generic UI click sound on the control panel (specific buttons keep their own)
patch(
    "        self._create_tray()\n",
    '        specific_buttons = {"投喂", "说话", "开心", "休息", "散步", "跟随", "静止", "隐藏"}\n'
    "        for button in self.control_panel.findChildren(QAbstractButton):\n"
    "            if button.text() in specific_buttons:\n"
    "                continue\n"
    '            button.clicked.connect(lambda _checked=False: self.sound.play("ui_click"))\n'
    "        self._create_tray()\n",
    "generic UI click sounds",
)

# 4) takeoff
patch(
    "        self.physics.launch(self.x(), self.y(), velocity_x, velocity_y)\n",
    '        self.physics.launch(self.x(), self.y(), velocity_x, velocity_y)\n        self.sound.play("takeoff")\n',
    "takeoff sound",
)

# 5) landing
patch(
    "        self.move(round(step.x), round(step.y))\n        if not step.settled:\n",
    '        self.move(round(step.x), round(step.y))\n'
    "        if step.first_impact:\n"
    '            self.sound.play("landing")\n'
    "        if not step.settled:\n",
    "landing sound",
)

# 6) panel / interaction sounds
patch(
    "    def _open_food_panel(self) -> None:\n        self._interrupt_activity()\n",
    '    def _open_food_panel(self) -> None:\n        self._interrupt_activity()\n        self.sound.play("pop")\n',
    "open food panel",
)
patch(
    "    def _say_daily_line(self) -> None:\n",
    '    def _say_daily_line(self) -> None:\n        self.sound.play("talk")\n',
    "talk sound",
)
patch(
    "        except ValueError:\n            return\n        self._interrupt_activity()\n",
    "        except ValueError:\n            return\n"
    '        sound_name = {\n'
    '            PetAction.HAPPY: "happy",\n'
    '            PetAction.SLEEPING: "rest",\n'
    '            PetAction.EATING: "feed",\n'
    '            PetAction.TALKING: "talk",\n'
    '            PetAction.ANGRY: "grumpy",\n'
    '            PetAction.THINKING: "ui_click",\n'
    '            PetAction.SWEEPING: "pop",\n'
    '            PetAction.DIZZY: "pop",\n'
    '        }.get(action, "pop")\n'
    "        self.sound.play(sound_name)\n"
    "        self._interrupt_activity()\n",
    "panel action sounds",
)
patch(
    "    def _hide_from_panel(self) -> None:\n        self.control_panel.hide()\n",
    '    def _hide_from_panel(self) -> None:\n        self.sound.play("hide")\n        self.control_panel.hide()\n',
    "hide sound",
)

# 7) mouse interactions
patch(
    "    def mouseDoubleClickEvent(self, event) -> None:\n"
    "        if event.button() != Qt.MouseButton.LeftButton:\n"
    "            return\n"
    "        self._click_timer.stop()\n"
    "        self._hold_timer.stop()\n",
    "    def mouseDoubleClickEvent(self, event) -> None:\n"
    "        if event.button() != Qt.MouseButton.LeftButton:\n"
    "            return\n"
    "        self._click_timer.stop()\n"
    "        self._hold_timer.stop()\n"
    '        self.sound.play("pop")\n',
    "double click sound",
)
patch(
    "        self._pending_click_region = outcome.body_region\n        self._click_timer.start(280)\n",
    '        self.sound.play("click")\n        self._pending_click_region = outcome.body_region\n        self._click_timer.start(280)\n',
    "click sound",
)
patch(
    '        if recent_count >= 3:\n            self._request_action(PetAction.ANGRY, reason="repeated_poke")\n',
    '        if recent_count >= 3:\n'
    '            self.sound.play("grumpy")\n'
    '            self._request_action(PetAction.ANGRY, reason="repeated_poke")\n',
    "grumpy on repeated poke",
)
patch(
    "        self._long_press_handled = True\n        self.pet_state.pet_head()\n",
    '        self._long_press_handled = True\n        self.sound.play("pop")\n        self.pet_state.pet_head()\n',
    "long press sound",
)
patch(
    "    def on_food(self, _food: str) -> None:\n        self._interrupt_activity()\n",
    '    def on_food(self, _food: str) -> None:\n        self._interrupt_activity()\n        self.sound.play("feed")\n',
    "feed sound",
)

# 8) mode buttons
patch(
    "    def set_mode(self, mode: str) -> None:\n        self._interrupt_activity(delay_seconds=1.5)\n",
    '    def set_mode(self, mode: str) -> None:\n'
    '        self.sound.play({"wander": "mode_wander", "follow": "mode_follow", "still": "mode_still"}.get(mode, "pop"))\n'
    "        self._interrupt_activity(delay_seconds=1.5)\n",
    "mode sounds",
)

# 9) tray / visibility / privacy
patch(
    "    def _open_control_panel_from_tray(self) -> None:\n        self._interrupt_activity()\n",
    '    def _open_control_panel_from_tray(self) -> None:\n        self.sound.play("pop")\n        self._interrupt_activity()\n',
    "tray panel pop",
)
patch(
    "    def toggle_visible(self) -> None:\n"
    "        if self.isVisible():\n"
    "            self._hidden_by_fullscreen = False\n"
    "            self.control_panel.hide()\n"
    "            self.hide()\n"
    "        else:\n"
    "            self.show()\n"
    "            self.raise_()\n",
    "    def toggle_visible(self) -> None:\n"
    "        if self.isVisible():\n"
    '            self.sound.play("hide")\n'
    "            self._hidden_by_fullscreen = False\n"
    "            self.control_panel.hide()\n"
    "            self.hide()\n"
    "        else:\n"
    '            self.sound.play("pop")\n'
    "            self.show()\n"
    "            self.raise_()\n",
    "show/hide sounds",
)
patch(
    "    def _show_privacy_notice(self) -> None:\n        QMessageBox.information(\n",
    '    def _show_privacy_notice(self) -> None:\n        self.sound.play("ui_click")\n        QMessageBox.information(\n',
    "privacy click",
)

with open(WINDOW, "w", encoding="utf-8", newline="\n") as f:
    f.write(text)

for status, label in PATCHES:
    print(f"{status:8s} {label}")
print("DONE", WINDOW, os.path.getsize(WINDOW), "bytes")
