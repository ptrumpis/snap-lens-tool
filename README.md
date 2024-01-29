[![GitHub License](https://img.shields.io/github/license/ptrumpis/snap-lens-tool)](https://github.com/ptrumpis/snap-lens-tool?tab=MIT-1-ov-file)
[![GitHub Release Date](https://img.shields.io/github/release-date/ptrumpis/snap-lens-tool)](https://github.com/ptrumpis/snap-lens-tool/releases/latest)
[![GitHub Release](https://img.shields.io/github/v/release/ptrumpis/snap-lens-tool)](https://github.com/ptrumpis/snap-lens-tool/releases/latest)
[![GitHub Commits](https://img.shields.io/github/commit-activity/t/ptrumpis/snap-lens-tool)](https://github.com/ptrumpis/snap-lens-tool/commits)
[![GitHub stars](https://img.shields.io/github/stars/ptrumpis/snap-lens-tool?style=flat)](https://github.com/ptrumpis/snap-lens-tool/stargazers) 
[![GitHub forks](https://img.shields.io/github/forks/ptrumpis/snap-lens-tool?style=flat)](https://github.com/ptrumpis/snap-lens-tool/forks)

# 👻 Snap Lens Tool

A Swiss Army Knife for Snapchat Lenses.

![Snap Lens Tool](https://github.com/ptrumpis/snap-lens-tool/assets/116500225/5210ef82-0239-481e-89c6-c59fe0f05bd9)

The code is based on the [Blender add-on for importing/exporting Snapchat lenses](https://github.com/cvirostek/snapchat-lens-blender-io) by [Connor Virostek](https://github.com/cvirostek).

Special thanks to user **ghalta22** for finding the fallback patch.

## ⭐ Features
- Select files or drag and drop them.
- Unpack Snapchat lenses.
- Re-Pack modified Snapchat lenses.
- Disable Snap Camera fallback mode on lenses.
- Download lenses from Snapchat.

![download](https://github.com/ptrumpis/snap-lens-tool/assets/116500225/3db4d46f-7d37-47bf-b4c5-8cba07687bad)

## 🚧 Planned Features (Work in Progress)
- Upload lens/cache to [Snap Camera Server](https://github.com/ptrumpis/snap-camera-server) (v0.8).
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

[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/ptrumpis)
[![Buy me a Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/ptrumpis)
[![Liberapay](https://img.shields.io/badge/Liberapay-F6C915?style=for-the-badge&logo=liberapay&logoColor=black)](https://liberapay.com/ptrumpis/)
[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.com/donate/?hosted_button_id=D2T92FVZAE65L)

You can also become my GitHub Sponsor  

[![Sponsor](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)](https://github.com/sponsors/ptrumpis)

## ℹ️ Notice: anti virus & malware reports
The binary file can produce a false positive by your anti virus software.
Please build your own binary according to the provided "Do It Yourself" instructions if you feel unsafe.

---

© 2023-2024 [Patrick Trumpis](https://github.com/ptrumpis)
