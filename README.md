# Path-IQ WSI Viewer (.svs)

A lightweight Whole Slide Image (WSI) viewer for `.svs` files using Flask, OpenSlide, and OpenSeadragon.

## Features

- Upload `.svs` slides from your browser
- Auto-generates Deep Zoom pyramids on the fly
- Pan and zoom smoothly in the browser
- Reuses generated tiles for faster reloads

## Requirements

- Python 3.10+
- OpenSlide runtime library installed on your system

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## Notes

- The app stores uploaded slides in `data/slides/`.
- Generated Deep Zoom tiles are stored in `data/cache/`.
- For production use, place this behind a proper WSGI server and configure upload limits.
