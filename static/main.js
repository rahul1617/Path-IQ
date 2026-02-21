const statusEl = document.getElementById("status");
const form = document.getElementById("upload-form");
const input = document.getElementById("slide-file");

const viewer = OpenSeadragon({
  id: "viewer",
  prefixUrl: "https://cdnjs.cloudflare.com/ajax/libs/openseadragon/4.1.0/images/",
  showNavigator: true,
  minZoomImageRatio: 0.8,
  visibilityRatio: 1,
  constrainDuringPan: true,
});

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b00" : "#0a5";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!input.files || !input.files[0]) {
    setStatus("Choose an .svs file first.", true);
    return;
  }

  const file = input.files[0];
  const body = new FormData();
  body.append("file", file);

  setStatus(`Uploading ${file.name}...`);

  try {
    const response = await fetch("/upload", { method: "POST", body });
    const payload = await response.json();

    if (!response.ok) {
      setStatus(payload.error || "Upload failed.", true);
      return;
    }

    const tileSource = `/slides/${payload.slide_id}.dzi`;
    viewer.open(tileSource);
    setStatus(`Loaded ${payload.name}`);
  } catch (error) {
    console.error(error);
    setStatus("Unexpected error while uploading slide.", true);
  }
});
