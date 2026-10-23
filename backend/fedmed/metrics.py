"""Segmentation metrics used for the centralized vs. federated audit."""

from __future__ import annotations

import numpy as np
import torch


def dice_score(
    prediction: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    ignore_index: int = 0,
    smooth: float = 1e-6,
) -> tuple[float, dict[int, float]]:
    """Compute per-class Dice similarity coefficients.

    Args:
        prediction: Integer class predictions, shape ``(B, ...)``.
        target: Integer ground-truth labels, shape ``(B, ...)``.
        num_classes: Total number of classes including background.
        ignore_index: Class excluded from the mean (background by default).
        smooth: Smoothing constant to avoid division by zero.

    Returns:
        ``(mean_dice, per_class_dice)`` where mean_dice excludes
        ``ignore_index`` and is expressed as a percentage.
    """
    pred = prediction.detach()
    tgt = target.detach()

    per_class: dict[int, float] = {}
    for c in range(1, num_classes):
        pred_c = (pred == c).float()
        tgt_c = (tgt == c).float()
        intersection = (pred_c * tgt_c).sum().item()
        denom = pred_c.sum().item() + tgt_c.sum().item()
        per_class[c] = (2.0 * intersection + smooth) / (denom + smooth)

    scored = [v for c, v in per_class.items() if c != ignore_index]
    mean = float(np.mean(scored) * 100.0) if scored else 0.0
    return mean, per_class


def dice_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    smooth: float = 1e-5,
) -> torch.Tensor:
    """Soft Dice loss over the foreground classes (differentiable)."""
    probs = torch.softmax(prediction, dim=1)
    one_hot = torch.nn.functional.one_hot(
        target.clamp(0, num_classes - 1), num_classes=num_classes
    )
    one_hot = one_hot.permute(0, 4, 1, 2, 3).float()

    dice = 0.0
    for c in range(1, num_classes):
        p = probs[:, c]
        t = one_hot[:, c]
        intersection = (p * t).sum()
        denom = p.sum() + t.sum()
        dice = dice + (1.0 - (2.0 * intersection + smooth) / (denom + smooth))

    return dice / max(num_classes - 1, 1)


def dice_ce_loss(
    prediction: torch.Tensor,
    target: torch.Tensor,
    num_classes: int,
    smooth: float = 1e-5,
    ce_weight: float = 1.0,
    dice_weight: float = 1.0,
) -> torch.Tensor:
    """Combined Dice + cross-entropy loss (MONAI ``DiceCELoss`` style).

    Dice alone over only the foreground classes lets the network ignore
    background entirely, which produces heavy over-segmentation and caps
    voxel accuracy near chance. Including a cross-entropy term over *all*
    classes (background included) supplies the per-voxel supervision that
    keeps the background calibrated, while Dice keeps the rare tumour
    classes from being swamped.
    """
    probs = torch.softmax(prediction, dim=1)
    one_hot = torch.nn.functional.one_hot(
        target.clamp(0, num_classes - 1), num_classes=num_classes
    )
    one_hot = one_hot.permute(0, 4, 1, 2, 3).float()

    dice_terms = []
    for c in range(1, num_classes):
        p = probs[:, c]
        t = one_hot[:, c]
        intersection = (p * t).sum()
        denom = p.sum() + t.sum()
        dice_terms.append(1.0 - (2.0 * intersection + smooth) / (denom + smooth))
    dice = torch.stack(dice_terms).mean()

    ce = torch.nn.functional.cross_entropy(prediction, target)

    return dice_weight * dice + ce_weight * ce


def pixel_accuracy(prediction: torch.Tensor, target: torch.Tensor) -> float:
    """Overall voxel accuracy as a percentage."""
    correct = (prediction == target).sum().item()
    total = target.numel()
    return 100.0 * correct / max(total, 1)


def evaluate_model(
    model: torch.nn.Module,
    loader: torch.utils.data.DataLoader,
    num_classes: int,
    device: torch.device | str = "cpu",
) -> dict:
    """Evaluate a model on a loader.

    Returns:
        Dict with ``dice``, ``loss``, ``accuracy`` and per-class dice scores.
    """
    model.eval()
    model.to(device)

    total_loss = 0.0
    batches = 0
    all_preds: list[torch.Tensor] = []
    all_targets: list[torch.Tensor] = []

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            total_loss += dice_loss(logits, labels, num_classes).item()
            batches += 1

            all_preds.append(torch.argmax(logits, dim=1).cpu())
            all_targets.append(labels.cpu())

    if batches == 0:
        return {"dice": 0.0, "loss": 0.0, "accuracy": 0.0, "per_class_dice": {}}

    preds = torch.cat(all_preds, dim=0)
    targets = torch.cat(all_targets, dim=0)

    mean_dice, per_class = dice_score(preds, targets, num_classes)
    accuracy = pixel_accuracy(preds, targets)

    return {
        "dice": round(mean_dice, 4),
        "loss": round(total_loss / batches, 6),
        "accuracy": round(accuracy, 4),
        "per_class_dice": {str(k): round(v * 100, 4) for k, v in per_class.items()},
    }
