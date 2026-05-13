from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from worker import start_download
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download", methods=["POST"])
def download():

    data = request.get_json()

    url = data.get("url")

    if not url:
        return jsonify({
            "success": False,
            "message": "URL kosong"
        })

    start_download(socketio, url)

    return jsonify({
        "success": True
    })


@app.route("/downloads/<filename>")
def downloads(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port
    )
