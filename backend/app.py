"""
Neuro-XAI Flask API — brain tumor classification (TensorFlow/Keras).

Class order (alphabetical): glioma(0), meningioma(1), notumor(2), pituitary(3)
"""

import io
import json
import os
import random
import socket
import traceback
import uuid
from datetime import datetime

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

from labels import (
    CLASS_FOLDERS,
    CONFIDENCE_THRESHOLD,
    DISPLAY_NAMES,
    PROBABILITY_KEYS,
    SEVERITY,
)

tf.random.set_seed(42)
np.random.seed(42)
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "brain_tumor_model.h5")
CLASS_INDICES_PATH = os.path.join(MODELS_DIR, "class_indices.json")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
IMAGE_SIZE = (224, 224)

EXPECTED_CLASS_INDICES = {
    "glioma": 0,
    "meningioma": 1,
    "notumor": 2,
    "pituitary": 3,
}

app = Flask(__name__)
CORS(
    app,
    origins=["*"],
    allow_headers=["Content-Type", "Accept"],
    methods=["GET", "POST", "OPTIONS"],
)

model = None
class_indices: dict[str, int] = {}
CLASS_NAMES: dict[int, str] = {}


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Accept")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response


def load_class_indices() -> dict[str, int]:
    if not os.path.exists(CLASS_INDICES_PATH):
        print(f"WARN: {CLASS_INDICES_PATH} not found — using default order")
        return dict(EXPECTED_CLASS_INDICES)

    with open(CLASS_INDICES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if data != EXPECTED_CLASS_INDICES:
        print("WARN: class_indices.json mismatch!")
        print(f"  Expected: {EXPECTED_CLASS_INDICES}")
        print(f"  Got:      {data}")
        print("  Retrain with: python train_model.py")

    print(f"Loaded class indices: {data}")
    return data


def load_brain_model() -> None:
    global model, class_indices, CLASS_NAMES

    class_indices = load_class_indices()
    CLASS_NAMES = {v: k for k, v in class_indices.items()}

    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        print("Run python train_model.py first!")
        model = None
        return

    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"Model loaded: {model.input_shape}")
    except Exception as e:
        print(f"ERROR loading model: {e}")
        model = None


def index_to_folder(idx: int) -> str:
    return CLASS_NAMES.get(idx, CLASS_FOLDERS[idx])


def preprocess_image(file_obj) -> np.ndarray:
    """Must match training: RGB, LANCZOS resize, EfficientNet preprocess_input."""
    img = Image.open(file_obj).convert("RGB")
    img = img.resize(IMAGE_SIZE, Image.LANCZOS)
    img_array = np.array(img, dtype=np.float32)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    assert img_array.shape == (1, 224, 224, 3), f"Bad shape: {img_array.shape}"
    return img_array


def build_probabilities(preds: np.ndarray) -> dict[str, float]:
    probs = {key: 0.0 for key in PROBABILITY_KEYS}
    for folder, idx in class_indices.items():
        display = DISPLAY_NAMES.get(folder, folder)
        if display in probs:
            probs[display] = round(float(preds[idx] * 100.0), 1)
    return probs


def run_prediction(file_obj, filename: str) -> tuple[dict, int]:
    if model is None:
        return {"error": "Model not loaded", "model_loaded": False}, 503

    batch = preprocess_image(file_obj)
    print(f"[DEBUG] Input shape: {batch.shape}")

    raw = model.predict(batch, verbose=0)[0]
    print(f"[DEBUG] Raw predictions: {raw}")

    class_idx = int(np.argmax(raw))
    confidence = float(raw[class_idx] * 100.0)
    folder = index_to_folder(class_idx)

    print(f"[DEBUG] Class index: {class_idx} ({folder})")
    print(f"[DEBUG] Confidence: {confidence:.2f}%")

    probabilities = build_probabilities(raw)
    tumor_type = DISPLAY_NAMES[folder]
    severity = SEVERITY[folder]
    message = None
    original_prediction = None
    original_confidence = None

    if confidence < CONFIDENCE_THRESHOLD:
        original_prediction = tumor_type
        original_confidence = confidence
        tumor_type = "Unclassified/Rare Tumor"
        severity = "None"
        message = (
            f"Low confidence ({confidence:.1f}%). "
            f"Model suggestion: {original_prediction}."
        )

    return {
        "predicted_class": class_idx,
        "predicted_label": tumor_type,
        "tumor_type": tumor_type,
        "confidence": round(confidence, 1),
        "severity": severity,
        "probabilities": probabilities,
        "filename": filename,
        "model_loaded": True,
        "message": message,
        "original_prediction": original_prediction,
        "original_confidence": original_confidence,
        "unclassified": confidence < CONFIDENCE_THRESHOLD,
    }, 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        os.makedirs(UPLOADS_DIR, exist_ok=True)

        if "file" not in request.files:
            return jsonify({"error": 'No file uploaded. Key must be "file"'}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        ext = os.path.splitext(file.filename)[1] or ".jpg"
        safe_name = (
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        )
        save_path = os.path.join(UPLOADS_DIR, safe_name)
        file.save(save_path)
        print(f"[INFO] Saved upload to {save_path}")

        with open(save_path, "rb") as saved_file:
            result, status = run_prediction(saved_file, safe_name)
        return jsonify(result), status
    except Exception as e:
        print("PREDICT ERROR:", traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


def pick_port(preferred: int = 5000) -> int:
    for port in range(preferred, preferred + 5):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except OSError:
                print(f"Port {port} is already in use.")
    return preferred


if __name__ == "__main__":
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    load_brain_model()

    port = pick_port(5000)
    if port != 5000:
        print("TIP: netstat -ano | findstr :5000  then  taskkill /PID <PID> /F")

    print(f"Starting Flask API on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
