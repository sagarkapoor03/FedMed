"""3D U-Net segmentation model (MONAI) for brain tumour segmentation."""

from __future__ import annotations

import torch
import torch.nn as nn
from monai.networks.nets import UNet

from .config import CONFIG


def build_model(num_classes: int | None = None) -> nn.Module:
    """Instantiate the 3D U-Net used by both the baseline and the FL nodes.

    The architecture is a MONAI ``UNet`` configured for volumetric (3D)
    inputs with a deep encoder/decoder stack appropriate for 64^3 patches.
    """
    cfg = CONFIG.model
    return UNet(
        spatial_dims=3,
        in_channels=cfg.in_channels,
        out_channels=num_classes or cfg.out_channels,
        channels=cfg.channels,
        strides=cfg.strides,
        num_res_units=cfg.num_res_units,
        dropout=cfg.dropout,
        norm="INSTANCE",
        bias=True,
        up_kernel_size=3,
    )


def count_parameters(model: nn.Module) -> int:
    """Total trainable parameter count (reported in the dashboard)."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_state_dict(model: nn.Module) -> dict[str, torch.Tensor]:
    """Return a plain (non-``nn.Module``) state dict for transport."""
    return {k: v.detach().cpu() for k, v in model.state_dict().items()}


def load_state_dict(model: nn.Module, state: dict[str, torch.Tensor]) -> None:
    """Load a transported state dict into a model instance."""
    model.load_state_dict({k: v.detach().cpu() for k, v in state.items()})
