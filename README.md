# ⚡ Lumina Remote Control v2.1.0 PRO

> A sleek, locally-hosted web dashboard that turns your phone into a full PC remote — with real-time System Monitoring, File Explorer, Process Manager, and a System Tray icon.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows)
![Version](https://img.shields.io/badge/Version-2.1.0%20PRO-7c6af5)

---

## ✨ Features

### v1.0.0 — Core Controls
| Category | Actions |
|---|---|
| 🔗 **Quick Links** | Open Hosting Panel, GitHub, YouTube in the PC browser |
| 🚀 **Launch Apps** | Start Telegram, VS Code, Notepad, Explorer |
| 🔊 **Volume Control** | Volume +10%, −10%, Mute toggle |
| 📸 **Screenshot** | Capture and view the screen on your phone |
| 🔒 **System Controls** | Lock, Sleep, Restart (10s), Shutdown (10s), Abort |

### v2.0.0 — Pro Modules
| Module | Description |
|---|---|
| 📊 **System Monitor** | Real-time CPU %, RAM used/total, Disk space with colour-coded progress bars |
| 📁 **File Explorer** | Browse Downloads, Desktop, Documents; tap any file to download it to your phone |
| ⚙️ **Process Manager** | View top 10 memory-hungry processes; kill any by PID with one tap |

### v2.1.0 — System Tray
| Feature | Description |
|---|---|
| 🖥️ **System Tray Icon** | Runs in the background with a tray icon (⚡) near the clock |
| 🖱️ **Tray Menu** | Right-click → Open Dashboard or Exit |
| 🌐 **Auto-open Browser** | Browser opens automatically on launch |

---

## 🖥️ Requirements

- **Windows 10 / 11**
- **Python 3.10+** - [python.org](https://python.org)
- All devices on the **same Wi-Fi network**

---

## 🚀 Quick Start (Executable)

Download `LuminaRemote.exe` from the [latest release](https://github.com/Andrey147-ai/lumina-remote/releases/latest) — no Python required. Just double-click and go.

---

## 🛠️ Installation from Source

### 1 — Clone the repository

```bash
git clone https://github.com/Andrey147-ai/lumina-remote.git
cd lumina-remote
```

### 2 — Create and activate a virtual environment

```bash
python -m venv .venv

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set your password

```powershell
$env:LUMINA_PASSWORD = "your-secret-password"
$env:LUMINA_SECRET   = "a-random-flask-secret-key"
python app.py
```

Or edit directly in `app.py`:

```python
ACCESS_PASSWORD = "your-secret-password"
```

### 5 — Run

```bash
python app.py
```

A tray icon ⚡ will appear near the clock and the browser will open automatically.

---

## 📱 Connecting from Your Phone

### Find your PC's local IP

```cmd
ipconfig
```

Look for **IPv4 Address**, e.g. `192.168.1.42`.

### Open in your phone's browser

```
http://192.168.1.42:5000
```

---

## 🔧 Customisation

### Adding folders to File Explorer

```python
EXPLORER_FOLDERS: dict[str, str] = {
    "Downloads": os.path.expanduser("~/Downloads"),
    "Projects":  r"C:\Users\Admin\Projects",   # ← add your own
}
```

### Adding Quick Links

```python
QUICK_LINKS: dict[str, str] = {
    "GitHub":  "https://github.com",
    "ChatGPT": "https://chat.openai.com",
}
```

---

## 📁 Project Structure

```
lumina-remote/
├── app.py                  # Main Flask server (v2.1.0)
├── requirements.txt
├── .gitignore
├── README.md
└── templates/
    ├── index.html          # Tabbed dashboard
    └── login.html          # Password login page
```

---

## 📋 Changelog

| Version | Changes |
|---|---|
| v2.1.0 | System tray icon, auto-open browser on launch |
| v2.0.2 | Fixed volume control for new pycaw versions |
| v2.0.1 | Fixed CoInitialize error for volume control |
| v2.0.0 | System Monitor, File Explorer, Process Manager, tabbed UI |
| v1.0.0 | Initial release |

---

## 🔒 Security

> **⚠️ Local network use only. Never expose port 5000 to the internet.**

- Change the default password before use
- File Explorer only serves folders listed in `EXPLORER_FOLDERS`
- Path traversal attacks are blocked server-side

---

## 📜 License

MIT — use it, modify it, make it yours.
