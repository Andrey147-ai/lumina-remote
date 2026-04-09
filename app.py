"""
Lumina Remote Control v2.0.0 — app.py
Adds: System Monitor (psutil), File Explorer & Downloader, Process Manager (Task Killer).
"""

import io
import os
import subprocess
import webbrowser
from functools import wraps
from pathlib import Path
from typing import Callable

import psutil
import pyautogui
from flask import (Flask, Response, jsonify, redirect, render_template,
                   request, send_from_directory, session, url_for)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

# ─── Configuration ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ACCESS_PASSWORD = os.environ.get("LUMINA_PASSWORD", "lumina2026")
SECRET_KEY      = os.environ.get("LUMINA_SECRET",   "change-me-to-something-random")

# ── Folders exposed in the File Explorer (label → absolute path) ──────────────
EXPLORER_FOLDERS: dict[str, str] = {
    "Downloads": os.path.expanduser("~/Downloads"),
    "Desktop":   os.path.expanduser("~/Desktop"),
    "Documents": os.path.expanduser("~/Documents"),
    # Add your own:
    # "Projects": r"C:\Users\Admin\Projects",
}

# ── Quick Links ───────────────────────────────────────────────────────────────
QUICK_LINKS: dict[str, str] = {
    "Hosting Panel": "https://hpanel.hostinger.com",
    "GitHub":        "https://github.com",
    "YouTube":       "https://youtube.com",
}

# ── App Paths ─────────────────────────────────────────────────────────────────
APP_PATHS: dict[str, list[str]] = {
    "Telegram":  [r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe"],
    "VS Code":   [r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"],
    "Notepad":   ["notepad.exe"],
    "Explorer":  ["explorer.exe"],
}

# ─── Flask App ────────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = SECRET_KEY


# ─── Auth Decorators ──────────────────────────────────────────────────────────

def login_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def api_auth(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ─── Pages ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template(
        "index.html",
        links=QUICK_LINKS,
        apps=list(APP_PATHS.keys()),
        folders=list(EXPLORER_FOLDERS.keys()),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password", "") == ACCESS_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "Wrong password — try again."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── API: Quick Links ─────────────────────────────────────────────────────────

@app.route("/api/open-url", methods=["POST"])
@api_auth
def open_url():
    data  = request.get_json(silent=True) or {}
    label = data.get("label", "")
    url   = QUICK_LINKS.get(label)
    if not url:
        return jsonify({"ok": False, "error": f"Unknown link: {label}"}), 400
    webbrowser.open(url)
    return jsonify({"ok": True, "message": f"Opened {label}"})


# ─── API: Launch Apps ─────────────────────────────────────────────────────────

@app.route("/api/launch-app", methods=["POST"])
@api_auth
def launch_app():
    data = request.get_json(silent=True) or {}
    name = data.get("app", "")
    cmd  = APP_PATHS.get(name)
    if not cmd:
        return jsonify({"ok": False, "error": f"Unknown app: {name}"}), 400
    try:
        subprocess.Popen([os.path.expandvars(c) for c in cmd], shell=False)
        return jsonify({"ok": True, "message": f"Launched {name}"})
    except FileNotFoundError:
        return jsonify({"ok": False, "error": f"Executable not found for {name}"}), 500


# ─── API: Screenshot ──────────────────────────────────────────────────────────

@app.route("/api/screenshot")
@api_auth
def screenshot():
    img = pyautogui.screenshot()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf, mimetype="image/png")


# ─── API: Volume ──────────────────────────────────────────────────────────────

def _volume_interface():
    devices   = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))


@app.route("/api/volume/<action>", methods=["POST"])
@api_auth
def volume(action: str):
    try:
        vol     = _volume_interface()
        current = vol.GetMasterVolumeLevelScalar()
        if action == "up":
            new = min(current + 0.10, 1.0)
            vol.SetMasterVolumeLevelScalar(new, None)
            msg = f"Volume up {int(new * 100)}%"
        elif action == "down":
            new = max(current - 0.10, 0.0)
            vol.SetMasterVolumeLevelScalar(new, None)
            msg = f"Volume down {int(new * 100)}%"
        elif action == "mute":
            muted = vol.GetMute()
            vol.SetMute(not muted, None)
            msg = "Unmuted" if muted else "Muted"
        else:
            return jsonify({"ok": False, "error": "Unknown action"}), 400
        return jsonify({"ok": True, "message": msg})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


# ─── API: System Controls ─────────────────────────────────────────────────────

@app.route("/api/system/<action>", methods=["POST"])
@api_auth
def system_control(action: str):
    cmds: dict[str, list[str]] = {
        "shutdown": ["shutdown", "/s", "/t", "10"],
        "restart":  ["shutdown", "/r", "/t", "10"],
        "sleep":    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        "lock":     ["rundll32.exe", "user32.dll,LockWorkStation"],
        "abort":    ["shutdown", "/a"],
    }
    cmd = cmds.get(action)
    if not cmd:
        return jsonify({"ok": False, "error": "Unknown action"}), 400
    try:
        subprocess.run(cmd, check=True)
        return jsonify({"ok": True, "message": f"System: {action} triggered"})
    except subprocess.CalledProcessError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


# =============================================================================
#  v2.0 NEW MODULES
# =============================================================================

# ─── API: System Monitor ──────────────────────────────────────────────────────

@app.route("/api/monitor/stats")
@api_auth
def monitor_stats():
    cpu  = psutil.cpu_percent(interval=0.3)
    ram  = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.splitdrive(BASE_DIR)[0] or "/")
    return jsonify({
        "ok": True,
        "cpu":  {"percent": cpu},
        "ram":  {"percent": ram.percent,
                 "used_gb":  round(ram.used  / 1024**3, 1),
                 "total_gb": round(ram.total / 1024**3, 1)},
        "disk": {"percent":  disk.percent,
                 "used_gb":  round(disk.used  / 1024**3, 1),
                 "total_gb": round(disk.total / 1024**3, 1),
                 "free_gb":  round(disk.free  / 1024**3, 1)},
    })


# ─── API: File Explorer ───────────────────────────────────────────────────────

@app.route("/api/files/list", methods=["POST"])
@api_auth
def file_list():
    data   = request.get_json(silent=True) or {}
    folder = data.get("folder", "")
    root   = EXPLORER_FOLDERS.get(folder)
    if not root:
        return jsonify({"ok": False, "error": f"Unknown folder: {folder}"}), 400
    root_path = Path(root)
    if not root_path.exists():
        return jsonify({"ok": False, "error": f"Folder not found: {root}"}), 404
    entries = []
    for item in sorted(root_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        try:
            stat = item.stat()
            entries.append({
                "name":    item.name,
                "is_file": item.is_file(),
                "size_kb": round(stat.st_size / 1024, 1) if item.is_file() else None,
            })
        except PermissionError:
            continue
    return jsonify({"ok": True, "folder": folder, "entries": entries})


@app.route("/api/files/download")
@api_auth
def file_download():
    folder   = request.args.get("folder", "")
    filename = request.args.get("name", "")
    root     = EXPLORER_FOLDERS.get(folder)
    if not root or not filename:
        return jsonify({"ok": False, "error": "Missing folder or filename"}), 400
    root_path   = Path(root).resolve()
    target_path = (root_path / filename).resolve()
    if not str(target_path).startswith(str(root_path)):
        return jsonify({"ok": False, "error": "Path traversal detected"}), 403
    return send_from_directory(str(root_path), filename, as_attachment=True)


# ─── API: Process Manager ─────────────────────────────────────────────────────

@app.route("/api/processes/list")
@api_auth
def process_list():
    procs = []
    for proc in psutil.process_iter(["pid", "name", "memory_info", "status"]):
        try:
            info = proc.info
            mem  = info["memory_info"]
            if mem is None:
                continue
            procs.append({
                "pid":    info["pid"],
                "name":   info["name"],
                "mem_mb": round(mem.rss / 1024**2, 1),
                "status": info["status"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    top10 = sorted(procs, key=lambda p: p["mem_mb"], reverse=True)[:10]
    return jsonify({"ok": True, "processes": top10})


@app.route("/api/processes/kill", methods=["POST"])
@api_auth
def process_kill():
    data = request.get_json(silent=True) or {}
    pid  = data.get("pid")
    if pid is None:
        return jsonify({"ok": False, "error": "No PID provided"}), 400
    try:
        proc = psutil.Process(int(pid))
        name = proc.name()
        proc.terminate()
        return jsonify({"ok": True, "message": f"Terminated {name} (PID {pid})"})
    except psutil.NoSuchProcess:
        return jsonify({"ok": False, "error": f"PID {pid} not found"}), 404
    except psutil.AccessDenied:
        return jsonify({"ok": False, "error": "Access denied — run as Administrator"}), 403
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
