# 👻 Snap Lens Tool

A Swiss Army Knife for Snapchat Lenses.

![Snap Lens Tool](https://github.com/ptrumpis/snap-lens-tool/assets/116500225/7c59e63b-5597-4375-bfc1-1785c386c6b0)

The code is based on the [Blender add-on for importing/exporting Snapchat lenses](https://github.com/cvirostek/snapchat-lens-blender-io) by [Connor Virostek](https://github.com/cvirostek).

## ⭐ Features
- Unpack Snapchat lenses.
- Re-Pack modified Snapchat lenses.

## 🚧 Planned Features (Work in Progress)
- Set Snap Camera fallback mode on lenses.
- Auto download missing lens assets.

## 🚀 Usage
[📥 Download](https://github.com/ptrumpis/snap-lens-tool/releases/latest) the latest binary or source files.

Run the script or the pre-build binary (if available).

See the information below to build your own binary.

## 🛠️ Do It Yourself Instructions
### 🧩 Install Python Dependencies
Install project dependencies from `requirements.txt` with **pip**

```sh
pip install -r requirements.txt
```

### 🎨 Edit GUI (optional)

Make changes to `dialog.ui` with **Qt Designer**
```sh
qt5-tools designer dialog.ui
```

Convert xml design representation to python code
```sh
pyuic5 -x dialog.ui -o src/qt/dialog.py
```

### ‍👨‍💻 Build binary (optional)

Install PyInstaller with **pip**
```sh
pip install pyinstaller
```

Create standalone binary with **PyInstaller**
```sh
pyinstaller --onedir --noconsole snap_lens_tool.py
```

Use `--onefile` instead of `--onedir` to output a single file.

The binary output files can be found under `./dist`.


## 💬 Community & Feedback
Please go here if you have questions or feedback:
- [💬 Snap Camera Discussions](https://github.com/ptrumpis/snap-camera-server/discussions)
- [🙏 Ask for Help](https://github.com/ptrumpis/snap-camera-server/discussions/categories/q-a)

And report code bugs here:
- [🐛 Report Bugs](https://github.com/ptrumpis/snap-lens-tool/issues)

## 🤝 Contributors
![GitHub Contributors Image](https://contrib.rocks/image?repo=ptrumpis/snap-lens-tool)

## ❤️ Support
If you like my work and want to support me, feel free to invite me for a virtual coffee ☕

- [☕ Ko-fi](https://ko-fi.com/ptrumpis)
- [☕ Buy me a Coffee](https://www.buymeacoffee.com/ptrumpis)
- [☕ Liberapay](https://liberapay.com/ptrumpis/)

You can also become my GitHub Sponsor

## ℹ️ Notice: anti virus & malware reports
The binary file can produce a false positive by your anti virus software.
Please build your own binary according to the provided "Do It Yourself" instructions if you feel unsafe.

---

© 2023 [Patrick Trumpis](https://github.com/ptrumpis)
