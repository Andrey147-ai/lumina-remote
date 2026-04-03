"""
Lumina Remote Control — app.py
A secure, locally-hosted web dashboard to control your Windows PC from any device on the same Wi-Fi.
"""

import io
import os
import subprocess
import webbrowser
from functools import wraps
from typing import Callable

import pyautogui
from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes

# ─── Configuration ────────────────────────────────────────────────────────────

ACCESS_PASSWORD = os.environ.get("LUMINA_PASSWORD", "lumina2024")
SECRET_KEY      = os.environ.get("LUMINA_SECRET",   "change-me-to-something-random")

# Customise these to your own paths / URLs
QUICK_LINKS: dict[str, str] = {
    "Hosting Panel": "https://hpanel.hostinger.com",
    "GitHub":        "https://github.com",
    "YouTube":       "https://youtube.com",
}

APP_PATHS: dict[str, list[str]] = {
    "Telegram":  [r"C:\Users\%USERNAME%\AppData\Roaming\Telegram Desktop\Telegram.exe"],
    "VS Code":   [r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe"],
    "Notepad":   ["notepad.exe"],
    "Explorer":  ["explorer.exe"],
}

# ─── Flask App ────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def login_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def api_login_required(f: Callable) -> Callable:
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
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        pwd = request.form.get("password", "")
        if pwd == ACCESS_PASSWORD:
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
@api_login_required
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
@api_login_required
def launch_app():
    data = request.get_json(silent=True) or {}
    name = data.get("app", "")
    cmd  = APP_PATHS.get(name)
    if not cmd:
        return jsonify({"ok": False, "error": f"Unknown app: {name}"}), 400
    try:
        # Expand %USERNAME% etc.
        expanded = [os.path.expandvars(c) for c in cmd]
        subprocess.Popen(expanded, shell=False)
        return jsonify({"ok": True, "message": f"Launched {name}"})
    except FileNotFoundError:
        return jsonify({"ok": False, "error": f"Executable not found for {name}"}), 500


# ─── API: Screenshot ──────────────────────────────────────────────────────────

@app.route("/api/screenshot")
@api_login_required
def screenshot():
    img    = pyautogui.screenshot()
    buf    = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(buf, mimetype="image/png")


# ─── API: Volume ──────────────────────────────────────────────────────────────

def _get_volume_interface():
    devices  = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))


@app.route("/api/volume/<action>", methods=["POST"])
@api_login_required
def volume(action: str):
    try:
        vol = _get_volume_interface()
        current = vol.GetMasterVolumeLevelScalar()

        if action == "up":
            vol.SetMasterVolumeLevelScalar(min(current + 0.10, 1.0), None)
            msg = f"Volume → {int(min(current + 0.10, 1.0) * 100)}%"
        elif action == "down":
            vol.SetMasterVolumeLevelScalar(max(current - 0.10, 0.0), None)
            msg = f"Volume → {int(max(current - 0.10, 0.0) * 100)}%"
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
@api_login_required
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


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # host="0.0.0.0" makes the server reachable on the local network
    app.run(host="0.0.0.0", port=5000, debug=False)
