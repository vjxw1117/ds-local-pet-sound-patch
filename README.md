# ds-local-pet 音效补丁（QQ弹弹）

给 [QCYTSN/ds-local-pet](https://github.com/QCYTSN/ds-local-pet) 大肥鱼桌宠添加 14 个“QQ弹弹”风格的交互音效。

本仓库**只包含补丁代码和原创音效**，不包含：

- 上游完整源码；
- 角色视觉素材（上游明确说明这些素材不在 MIT 范围内）；
- 打包好的 exe / PySide6 运行库。

## 包含内容

```text
sound.py                 # 音效播放模块（QSoundEffect，winsound 兜底）
apply_sound_patch.py     # 自动把音效调用注入 pet/window.py
sounds/                  # 14 个原创 WAV 音效
README.md
LICENSE                  # 本补丁代码的 MIT 许可证
THIRD_PARTY_NOTICES.md
.gitignore
```

## 使用方法

需要 Python 3.11+。

```bash
# 1. 克隆上游项目
git clone https://github.com/QCYTSN/ds-local-pet.git
cd ds-local-pet

# 2. 把本仓库的 sound.py、apply_sound_patch.py 复制到项目根目录
# 3. 把本仓库的 sounds/ 整个复制到项目根目录
# 4. 运行补丁脚本（在项目根目录）
python apply_sound_patch.py

# 5. 安装依赖并运行
pip install -r requirements.txt
python main.py
```

补丁脚本是幂等的：重复运行不会重复插入。

## 音效映射

| 动作 | 音效 |
|---|---|
| 单击桌宠 | `click.wav` |
| 拖拽甩出 / 掉落 | `takeoff.wav` |
| 落地 / 重摔 | `landing.wav` |
| 投喂 | `feed.wav` |
| 说话 | `talk.wav` |
| 开心 | `happy.wav` |
| 休息 | `rest.wav` |
| 散步 / 跟随 / 静止 | `mode_wander.wav` / `mode_follow.wav` / `mode_still.wav` |
| 更多设置、大小、开关等 | `ui_click.wav` |
| 隐藏 | `hide.wav` |
| 连续戳到闹脾气 | `grumpy.wav` |
| 双击 / 其他 | `pop.wav` |

音量可以在 `sound.py` 的 `VOLUMES` 字典里调整。

## 许可证与致谢

- 本补丁代码：MIT，见 `LICENSE`。
- 上游项目 [QCYTSN/ds-local-pet](https://github.com/QCYTSN/ds-local-pet)：代码 MIT；**角色视觉素材不适用 MIT，本仓库不再分发**。
- PySide6 / Qt：LGPL / 商业双许可，由使用者自行通过 `pip install PySide6` 安装。
- 14 个 WAV 由本项目用 Python 标准库程序生成，作为原创音效随本仓库以 MIT 发布。

