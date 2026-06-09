"""
Train brain tumor classifier — EfficientNetB0 transfer learning.

Training:   backend/BrainTumorDataset/Training/
Validation: backend/BrainTumorDataset/Testing/

Class order (alphabetical): glioma=0, meningioma=1, notumor=2, pituitary=3
"""

from __future__ import annotations

import json
import os

import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from labels import CLASS_FOLDERS

tf.random.set_seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR = os.path.join(BASE_DIR, "BrainTumorDataset", "Training")
VAL_DIR = os.path.join(BASE_DIR, "BrainTumorDataset", "Testing")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "brain_tumor_model.h5")
INDICES_PATH = os.path.join(MODELS_DIR, "class_indices.json")

EPOCHS = 15
BATCH_SIZE = 32
IMG_SIZE = (224, 224)

EXPECTED_CLASS_INDICES = {name: idx for idx, name in enumerate(CLASS_FOLDERS)}


def build_model(num_classes: int = 4) -> tf.keras.Model:
    """EfficientNetB0 backbone (ImageNet) + trainable classification head."""
    base = EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_shape=(*IMG_SIZE, 3),
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
    x = base(inputs, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax")(x)

    return tf.keras.Model(inputs, outputs)


def make_generators():
    """Load train/val data with augmentation and EfficientNet preprocessing."""
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=20,
        width_shift_range=0.15,
        height_shift_range=0.15,
        horizontal_flip=True,
        zoom_range=0.15,
        brightness_range=(0.8, 1.2),
    )
    val_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)

    flow_kwargs = {
        "target_size": IMG_SIZE,
        "batch_size": BATCH_SIZE,
        "class_mode": "categorical",
        "classes": CLASS_FOLDERS,
    }

    train_gen = train_datagen.flow_from_directory(
        TRAIN_DIR,
        shuffle=True,
        seed=42,
        **flow_kwargs,
    )
    val_gen = val_datagen.flow_from_directory(
        VAL_DIR,
        shuffle=False,
        **flow_kwargs,
    )
    return train_gen, val_gen


def main() -> None:
    if not os.path.isdir(TRAIN_DIR):
        raise FileNotFoundError(f"Training data not found: {TRAIN_DIR}")
    if not os.path.isdir(VAL_DIR):
        raise FileNotFoundError(f"Validation data not found: {VAL_DIR}")

    os.makedirs(MODELS_DIR, exist_ok=True)

    train_gen, val_gen = make_generators()

    print("Class indices:", train_gen.class_indices)
    print("Training samples:", train_gen.samples)
    print("Validation samples:", val_gen.samples)

    if train_gen.class_indices != EXPECTED_CLASS_INDICES:
        raise ValueError(
            "Unexpected class order!\n"
            f"  Expected: {EXPECTED_CLASS_INDICES}\n"
            f"  Got:      {train_gen.class_indices}"
        )

    with open(INDICES_PATH, "w", encoding="utf-8") as f:
        json.dump(train_gen.class_indices, f, indent=2)
    print(f"Saved class indices to {INDICES_PATH}")

    model = build_model(num_classes=len(CLASS_FOLDERS))
    model.compile(
        optimizer=Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()

    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        ModelCheckpoint(
            MODEL_PATH,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]

    print(f"\nTraining for up to {EPOCHS} epochs (early stopping enabled)...\n")
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=EPOCHS,
        callbacks=callbacks,
        verbose=1,
    )

    for epoch, (train_acc, val_acc) in enumerate(
        zip(history.history["accuracy"], history.history["val_accuracy"]), start=1
    ):
        print(
            f"Epoch {epoch}/{len(history.history['accuracy'])} summary — "
            f"train acc: {train_acc * 100:.2f}%, val acc: {val_acc * 100:.2f}%"
        )

    model.save(MODEL_PATH)
    print(f"\nBest model saved to {MODEL_PATH}")

    val_loss, val_acc = model.evaluate(val_gen, verbose=0)
    print(f"Final validation accuracy: {val_acc * 100:.2f}%")
    print(f"Final validation loss: {val_loss:.4f}")


if __name__ == "__main__":
    main()
