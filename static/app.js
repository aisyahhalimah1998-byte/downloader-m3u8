// static/app.js

const socket = io();

const button = document.getElementById("downloadBtn");
const urlInput = document.getElementById("url");
const logs = document.getElementById("logs");
const statusDiv = document.getElementById("status");

button.addEventListener("click", async () => {

    const url = urlInput.value.trim();

    if (!url) {
        alert("Masukan URL M3U8");
        return;
    }

    logs.innerHTML = "";
    statusDiv.innerText = "Downloading...";

    const response = await fetch("/download", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            url: url
        })
    });

    const result = await response.json();

    if (!result.success) {
        statusDiv.innerText = "Error";
    }

});

socket.on("log", data => {

    logs.innerHTML += `
        <div>${data.message}</div>
    `;

    logs.scrollTop = logs.scrollHeight;

});

socket.on("done", data => {

    if (data.success) {

        statusDiv.innerHTML = `
            Download selesai:
            <a href="/downloads/${data.file}" target="_blank">
                Download File
            </a>
        `;

    } else {

        statusDiv.innerText = "Download gagal";

    }

});
