# 👻 Snap Lens Tool

A Swiss Army Knife for Snapchat Lenses.

![Snap Lens Tool](https://github.com/ptrumpis/snap-lens-tool/assets/116500225/7c59e63b-5597-4375-bfc1-1785c386c6b0)

The code is based on the [Blender add-on for importing/exporting Snapchat lenses](https://github.com/cvirostek/snapchat-lens-blender-io) by [Connor Virostek](https://github.com/cvirostek).

Special thanks to user **ghalta22** for finding the fallback patch.

## ⭐ Features
- Unpack Snapchat lenses.
- Re-Pack modified Snapchat lenses.
- Disable Snap Camera fallback mode on lenses.
- Download lenses from Snapchat

## 🚧 Planned Features (Work in Progress)
- Upload lens/cache to Snap Camera Server (v0.8).
- Auto download missing lens assets (v0.9).
- Fix "Unknown blend mode" (v1.0).
- Fix AMD display bug (v1.x).

## 🚀 Usage
You can run the script or download a pre-build binary.

- [📥 Download](https://github.com/ptrumpis/snap-lens-tool/releases/latest) and run the latest pre-build binary (if available).
- 📜 Download the source and run the `snap_lens_tool.py` script yourself (see below).

If you just want to unpack files take a look at [Web based online tool for unpacking lenses](https://ptrumpis.github.io/snap-lens-file-extractor/).

### Development & Build Instructions
Please see the [🛠️ Do It Yourself Instructions](docs/DO_IT_YOURSELF.md) for development and to build your own binary.

### Run the script
You need to have *Python 3* installed, and you need to install the requirements with *pip*:
```sh
pip install -r requirements.txt
```

You can start **Snap Lens Tool** with:
```sh
python snap_lens_tool.py
```

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
