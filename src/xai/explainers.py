"""Explainability helpers."""

import numpy as np


class GradCAMExplainer:
    def __init__(self, model):
        self.model = model

    def explain(self, image_tensor, target_class):
        """Return placeholder heatmap when full Grad-CAM weights unavailable."""
        try:
            arr = image_tensor[0].permute(1, 2, 0).detach().cpu().numpy()
            arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-8)
            heat = np.uint8(arr * 255)
            overlay = np.uint8(arr * 0.6 * 255 + np.array([0.2, 0.0, 0.3]) * 255 * 0.4)
            return heat, overlay
        except Exception:
            return None, None
