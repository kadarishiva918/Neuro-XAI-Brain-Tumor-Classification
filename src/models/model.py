"""Brain tumor classification model."""

import torch
import torch.nn as nn
from torchvision import models


class BrainTumorClassifier(nn.Module):
    """EfficientNet-based classifier with optional attention flag."""

    def __init__(
        self,
        backbone: str = "efficientnet_b0",
        num_classes: int = 4,
        pretrained: bool = False,
        use_attention: bool = True,
    ):
        super().__init__()
        self.use_attention = use_attention
        weights = "DEFAULT" if pretrained else None

        if backbone in ("efficientnet_b0", "EfficientNet-B0"):
            self.features = models.efficientnet_b0(weights=weights)
            in_features = self.features.classifier[1].in_features
            self.features.classifier = nn.Identity()
        else:
            self.features = models.mobilenet_v2(weights=weights)
            in_features = self.features.classifier[1].in_features
            self.features.classifier = nn.Identity()

        self.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(in_features, num_classes),
        )

    def forward(self, x):
        features = self.features(x)
        if isinstance(features, tuple):
            features = features[0]
        return self.classifier(features)
