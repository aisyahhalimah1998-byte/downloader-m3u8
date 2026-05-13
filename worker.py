# worker.py

import os
import uuid
import subprocess
from flask_socketio import emit

DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_m3u8(socketio, url):
    try:
        filename = f"{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, filename)

        cmd = [
            "ffmpeg",
            "-i", url,
            "-c", "copy",
            "-bsf:a", "aac_adtstoasc",
            output_path
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        for line in process.stdout:
            socketio.emit("log", {"message": line})

        process.wait()

        if process.returncode == 0:
            socketio.emit("done", {
                "success": True,
                "file": filename
            })
        else:
            socketio.emit("done", {
                "success": False
            })

    except Exception as e:
        socketio.emit("done", {
            "success": False,
            "error": str(e)
        })
