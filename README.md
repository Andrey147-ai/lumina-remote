# ⚡ Lumina Remote Control v2.0 PRO

> A sleek, locally-hosted web dashboard that turns your phone into a full PC remote — now with real-time System Monitoring, a File Explorer & Downloader, and a Process Manager (Task Killer).

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows)
![Version](https://img.shields.io/badge/Version-2.0.0%20PRO-7c6af5)

---

## ✨ Features

### v1.0 — Core Controls
| Category | Actions |
|---|---|
| 🔗 **Quick Links** | Open Hosting Panel, GitHub, YouTube in the PC browser |
| 🚀 **Launch Apps** | Start Telegram, VS Code, Notepad, Explorer |
| 🔊 **Volume Control** | Volume +10%, −10%, Mute toggle |
| 📸 **Screenshot** | Capture and view the screen on your phone |
| 🔒 **System Controls** | Lock, Sleep, Restart (10s), Shutdown (10s), Abort |

### v2.0 — Pro Modules
| Module | Description |
|---|---|
| 📊 **System Monitor** | Real-time CPU %, RAM used/total, Disk used/free with colour-coded progress bars |
| 📁 **File Explorer** | Browse Downloads, Desktop, Documents; tap any file to download it directly to your phone |
| ⚙️ **Process Manager** | View the top 10 most memory-hungry processes; kill any process by PID with one tap |

---

## 🖥️ Requirements

- **Windows 10 / 11**
- **Python 3.10+** — [python.org](https://python.org)
- All devices on the **same Wi-Fi network**

---

## 🚀 Installation

### 1 — Clone the repository

```bash
git clone https://github.com/your-username/lumina-remote.git
cd lumina-remote
```

### 2 — Create and activate a virtual environment

```bash
python -m venv .venv

# Windows CMD
.venv\Scripts\activate.bat

# Windows PowerShell (if scripts are blocked, run this first):
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set your password *(important!)*

```powershell
# PowerShell
$env:LUMINA_PASSWORD = "your-secret-password"
$env:LUMINA_SECRET   = "a-random-flask-secret-key"
python app.py
```

Or edit directly in `app.py` (quick test only):

```python
ACCESS_PASSWORD = "your-secret-password"
```

### 5 — Customise folders, apps, and links

Open `app.py` and edit the dictionaries at the top:

```python
EXPLORER_FOLDERS: dict[str, str] = {
    "Downloads": os.path.expanduser("~/Downloads"),
    "Projects":  r"C:\Users\Admin\Projects",   # ← add your own
}

QUICK_LINKS: dict[str, str] = {
    "GitHub":    "https://github.com",
    "ChatGPT":   "https://chat.openai.com",    # ← add your own
}
```

### 6 — Run

```bash
python app.py
```

---

## 📱 Connecting from Your Phone

### Find your PC's local IP

Open **Command Prompt** and run:

```cmd
ipconfig
```

Look for **IPv4 Address** under your Wi-Fi adapter, e.g. `192.168.1.42`.

### Open in your phone's browser

```
http://192.168.1.42:5000
```

Enter your password, bookmark it, done.

---

## 📊 v2.0 Module Details

### System Monitor
- Auto-loads when you switch to the Monitor tab
- Progress bars turn **amber** at 65% and **red** at 85% usage
- Hit **↻ Refresh** for an updated snapshot

### File Explorer
- Exposes only the folders listed in `EXPLORER_FOLDERS` — nothing else is accessible
- Folders and files are sorted alphabetically (folders first)
- Tap **⬇ DL** next to any file to download it straight to your phone

### Process Manager
- Shows the top 10 processes by RSS memory usage
- Tap **✕ Kill** → confirm → the process is sent `SIGTERM` via `psutil.Process.terminate()`
- System-level processes (e.g. `System`, `smss.exe`) will return **Access Denied** unless you run the server as Administrator

---

## 📁 Project Structure

```
lumina-remote/
├── app.py                  # Main Flask server (v2.0)
├── requirements.txt
├── .gitignore
├── README.md
└── templates/
    ├── index.html          # Tabbed dashboard (Control / Monitor / Files / Processes)
    └── login.html          # Password login page
```

---

## 🔒 Security Considerations

> **⚠️ This server is intended for local/home network use only.**

1. **Never expose port 5000 to the internet.** Do not port-forward it in your router.
2. **Use a strong password.** Change `LUMINA_PASSWORD` before using the app.
3. **File access is sandboxed.** The File Explorer only serves files from the folders listed in `EXPLORER_FOLDERS`. Path-traversal attacks are blocked server-side.
4. **Process kill requires privilege.** To kill system processes, run the server as Administrator — but only do so if you understand the implications.
5. **Do not commit secrets.** Never hardcode passwords in files you push to Git.

---

## 📜 License

MIT — use it, modify it, make it yours.
