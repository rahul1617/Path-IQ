from __future__ import annotations

import hashlib
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

import openslide
from openslide.deepzoom import DeepZoomGenerator

BASE_DIR = Path(__file__).resolve().parent
SLIDES_DIR = BASE_DIR / "data" / "slides"
CACHE_DIR = BASE_DIR / "data" / "cache"
ALLOWED_EXTENSIONS = {"svs"}

SLIDES_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 6 * 1024 * 1024 * 1024  # 6 GB


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def slide_id_for_path(slide_path: Path) -> str:
    return hashlib.sha256(str(slide_path).encode("utf-8")).hexdigest()[:16]


def get_slide_paths(slide_id: str) -> tuple[Path, Path]:
    metadata_path = CACHE_DIR / f"{slide_id}.txt"
    if not metadata_path.exists():
        raise FileNotFoundError("Unknown slide id")

    slide_path = Path(metadata_path.read_text(encoding="utf-8").strip())
    if not slide_path.exists():
        raise FileNotFoundError("Slide no longer exists")

    return slide_path, metadata_path


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload_slide():
    upload = request.files.get("file")
    if upload is None or upload.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(upload.filename):
        return jsonify({"error": "Only .svs files are supported"}), 400

    filename = secure_filename(upload.filename)
    slide_path = SLIDES_DIR / filename
    upload.save(slide_path)

    slide_id = slide_id_for_path(slide_path)
    metadata_path = CACHE_DIR / f"{slide_id}.txt"
    metadata_path.write_text(str(slide_path), encoding="utf-8")

    return jsonify({"slide_id": slide_id, "name": filename})


@app.get("/slides/<slide_id>.dzi")
def slide_dzi(slide_id: str):
    slide_path, _ = get_slide_paths(slide_id)

    with openslide.OpenSlide(str(slide_path)) as slide:
        dz = DeepZoomGenerator(slide, tile_size=256, overlap=1, limit_bounds=True)
        return app.response_class(dz.get_dzi("jpeg"), mimetype="application/xml")


@app.get("/slides/<slide_id>_files/<int:level>/<int:col>_<int:row>.jpeg")
def slide_tile(slide_id: str, level: int, col: int, row: int):
    slide_path, _ = get_slide_paths(slide_id)

    with openslide.OpenSlide(str(slide_path)) as slide:
        dz = DeepZoomGenerator(slide, tile_size=256, overlap=1, limit_bounds=True)
        tile = dz.get_tile(level, (col, row))

    tiles_dir = CACHE_DIR / f"{slide_id}_files" / str(level)
    tiles_dir.mkdir(parents=True, exist_ok=True)
    tile_path = tiles_dir / f"{col}_{row}.jpeg"

    if not tile_path.exists():
        tile.save(tile_path, format="JPEG", quality=85)

    return send_from_directory(tiles_dir, tile_path.name, mimetype="image/jpeg")


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=True)
