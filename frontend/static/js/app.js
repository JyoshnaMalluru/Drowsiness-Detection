const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const alertBox = document.getElementById("alertBox");
const alertSound = document.getElementById("alertSound");
const videoIcon = document.getElementById("videoIcon");

const drowsyStatus = document.getElementById("drowsyStatus");
const earValueElem = document.getElementById("earValue");
const flagCountElem = document.getElementById("flagCount");

const socket = io("http://localhost:5000");
let streaming = false;
let stream = null;
let intervalId = null;

socket.on("connect", () => console.log("Connected:", socket.id));

socket.on("status", data => {
  if (data.drowsy) {
    alertBox.style.display = "block";
    if (alertSound.paused) alertSound.play();
  } else {
    alertBox.style.display = "none";
    alertSound.pause();
    alertSound.currentTime = 0;
  }

  drowsyStatus.textContent = data.drowsy ? "DROWSY" : "ALERT";
  earValueElem.textContent = data.ear !== null ? data.ear.toFixed(3) : "-";
  flagCountElem.textContent = data.flag;
});

startBtn.addEventListener("click", () => {
  if (streaming) return;
  streaming = true;

  videoIcon.style.display = "none";

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(s => {
      stream = s;
      video.srcObject = stream;

      intervalId = setInterval(() => {
        if (video.videoWidth === 0) return;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        const dataURL = canvas.toDataURL("image/jpeg");
        socket.emit("frame", dataURL);
      }, 100);
    })
    .catch(err => console.error("Camera error:", err));
});

stopBtn.addEventListener("click", () => {
  if (!streaming) return;
  streaming = false;

  videoIcon.style.display = "block";

  clearInterval(intervalId);
  intervalId = null;

  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    video.srcObject = null;
  }

  alertBox.style.display = "none";
  alertSound.pause();
  alertSound.currentTime = 0;

  drowsyStatus.textContent = "-";
  earValueElem.textContent = "-";
  flagCountElem.textContent = "-";
});