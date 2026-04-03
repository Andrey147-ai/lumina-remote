# ⚡ Lumina Remote Control

> A sleek, locally-hosted web dashboard that turns your phone into a full PC remote — within your home Wi-Fi network.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Category | Actions |
|---|---|
| 🔗 **Quick Links** | Open Hosting Panel, GitHub, YouTube in the PC's default browser |
| 🚀 **Launch Apps** | Start Telegram, VS Code, Notepad, Explorer |
| 🔊 **Volume Control** | Volume +10%, −10%, Mute toggle |
| 📸 **Screenshot** | Capture the current screen and view it on your phone |
| 🔒 **System Controls** | Lock, Sleep, Restart (10s), Shutdown (10s), Abort |
| 🛡️ **Security** | Session-based password login; all API routes protected |

---

## 🖥️ Requirements

- **Windows 10 / 11**
- **Python 3.10+** — [python.org](https://python.org)
- All devices on the **same Wi-Fi network**

---

## 🚀 Installation

### 1 — Clone the repository

```bash
git clone https://github.com/Andrey147-ai/lumina-remote.git
cd lumina-remote
```

### 2 — Create and activate a virtual environment

```bash
# Create
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set your password *(important!)*

Option A — environment variable (recommended):

```powershell
# PowerShell
$env:LUMINA_PASSWORD = "your-secret-password"
$env:LUMINA_SECRET   = "a-random-flask-secret-key"
```

Option B — edit directly in `app.py` (quick test only, not for shared machines):

```python
ACCESS_PASSWORD = "your-secret-password"
SECRET_KEY      = "a-random-flask-secret-key"
```

### 5 — Customise your apps and links *(optional)*

Open `app.py` and edit the `QUICK_LINKS` and `APP_PATHS` dictionaries at the top of the file to match your own applications and favourite URLs.

### 6 — Run the server

```bash
python app.py
```

You should see:

```
 * Running on http://0.0.0.0:5000
```

---

## 📱 Connecting from Your Phone

### Find your PC's local IP address

Open **Command Prompt** (`Win + R` → `cmd`) and run:

```cmd
ipconfig
```

Look for **IPv4 Address** under your active network adapter (usually **Wi-Fi**). It will look like:

```
IPv4 Address. . . . . . : 192.168.1.42
```

### Open in your phone's browser

```
http://192.168.1.42:5000
```

Enter your password and you're in. Bookmark it for quick access!

---

## 🔧 Customisation

### Adding more Quick Links

```python
QUICK_LINKS: dict[str, str] = {
    "Hosting Panel": "https://hpanel.hostinger.com",
    "GitHub":        "https://github.com",
    "YouTube":       "https://youtube.com",
    "ChatGPT":       "https://chat.openai.com",   # ← add here
}
```

### Adding more Apps

```python
APP_PATHS: dict[str, list[str]] = {
    ...
    "Spotify": [r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"],
}
```

---

## 🔒 Security Considerations

> **⚠️ This server is intended for local/home network use only.**

Please read and understand the following before use:

1. **Never expose port 5000 to the internet.** Do not forward this port in your router settings, do not use it with a public-facing proxy without adding proper HTTPS and authentication.

2. **Use a strong, unique password.** The default `lumina2024` is a placeholder. Change it via the `LUMINA_PASSWORD` environment variable before using the app.

3. **The shutdown/restart buttons have a 10-second window.** Use the "Abort" button to cancel if triggered accidentally.

4. **Session tokens are in-memory.** Restarting the server invalidates all sessions. Set `LUMINA_SECRET` to a long random string to keep sessions valid across restarts if needed.

5. **Do not commit your `.env` file or hardcoded passwords** to version control. The included `.gitignore` excludes `.env` files automatically.

---

## 📁 Project Structure

```
lumina-remote/
├── app.py                  # Main Flask server
├── requirements.txt        # Python dependencies
├── .gitignore
├── README.md
└── templates/
    ├── index.html          # Main dashboard (dark, mobile-responsive)
    └── login.html          # Password login page
```

---

## 📜 License

MIT — use it, modify it, make it yours.
