#!/usr/bin/env python3
"""
create_bubble_asset.py
Renders a high-quality 3D glossy pill/bubble card as a PNG asset.
Output: bubble_card_instagram.png  (962 × 502 px, RGBA)

Run once to regenerate the asset whenever you want a new look.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import os

# ── Output ────────────────────────────────────────────────────────────────────
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PATH   = os.path.join(ASSETS_DIR, 'bubble_card_instagram.png')

# ── Card dimensions (matches instagram apply_info_overlay geometry) ───────────
CARD_W  = 962
CARD_H  = 502
RADIUS  = 26   # corner radius

# ── Brand colour — Ship Cove #6D8CBA ─────────────────────────────────────────
BASE_R, BASE_G, BASE_B = 109, 140, 186


# ─────────────────────────────────────────────────────────────────────────────

def make_rounded_mask(W: int, H: int, R: int) -> np.ndarray:
    """Return float32 alpha mask with rounded corners, values 0–1."""
    img  = Image.new('L', (W, H), 0)
    d    = ImageDraw.Draw(img)
    d.rectangle([R, 0, W - R, H],     fill=255)
    d.rectangle([0, R, W,     H - R], fill=255)
    d.ellipse([0,       0,       R*2,   R*2],   fill=255)
    d.ellipse([W - R*2, 0,       W,     R*2],   fill=255)
    d.ellipse([0,       H - R*2, R*2,   H],     fill=255)
    d.ellipse([W - R*2, H - R*2, W,     H],     fill=255)
    return np.array(img, dtype=np.float32) / 255.0


def gaussian_ellipse(yn, xn,
                     cx: float, cy: float,
                     rx: float, ry: float,
                     sharpness: float = 2.5) -> np.ndarray:
    """Gaussian-falloff ellipse centred at (cx, cy), broadcast-safe."""
    d = ((xn - cx) / rx) ** 2 + ((yn - cy) / ry) ** 2
    return np.exp(-d * sharpness)


def make_bubble() -> Image.Image:
    H, W = CARD_H, CARD_W
    yn   = np.linspace(0, 1, H)[:, np.newaxis]   # (H, 1)
    xn   = np.linspace(0, 1, W)[np.newaxis, :]   # (1, W)

    # ── 1. Base vertical gradient ─────────────────────────────────────────────
    # Top ≈ 28% brighter than base, bottom ≈ 28% darker  →  curved surface feel
    ones  = np.ones((H, W), dtype=np.float32)
    shade = (1.28 - 0.56 * yn) * ones    # broadcast to (H, W)
    r = BASE_R * shade
    g = BASE_G * shade
    b = BASE_B * shade

    # ── 2. Large primary specular (diffuse gloss across top ~55%) ────────────
    spec1 = gaussian_ellipse(yn, xn, cx=0.50, cy=0.20, rx=0.45, ry=0.28,
                             sharpness=1.8) * 0.80
    r += spec1 * 255
    g += spec1 * 255
    b += spec1 * 255

    # ── 3. Tight bright specular (hot spot — very top centre) ────────────────
    spec2 = gaussian_ellipse(yn, xn, cx=0.50, cy=0.06, rx=0.20, ry=0.07,
                             sharpness=2.0) * 0.70
    r += spec2 * 255
    g += spec2 * 255
    b += spec2 * 255

    # ── 4. Micro rim highlight (crisp white line along top edge) ─────────────
    rim = np.clip(1.0 - yn / 0.022, 0, 1) ** 1.5 * 0.60
    r  += rim * 255
    g  += rim * 255
    b  += rim * 255

    # ── 5. Bottom ambient shadow ──────────────────────────────────────────────
    darken = np.clip((yn - 0.70) / 0.30, 0, 1) ** 1.8 * 0.32
    r *= (1 - darken)
    g *= (1 - darken)
    b *= (1 - darken)

    # ── 6. Left edge cool tint (adds subtle depth/dimension) ─────────────────
    edge_l = np.clip(1.0 - xn / 0.06, 0, 1) ** 2.0 * 0.12
    r *= (1 - edge_l)
    g *= (1 - edge_l)
    b  = np.clip(b * (1 - edge_l * 0.5), 0, 255)  # blue channel stays warm

    r = np.clip(r, 0, 255)
    g = np.clip(g, 0, 255)
    b = np.clip(b, 0, 255)

    # ── 7. Rounded rect alpha mask ────────────────────────────────────────────
    mask = make_rounded_mask(W, H, RADIUS)

    # ── 8. Assemble RGBA ──────────────────────────────────────────────────────
    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[:, :, 0] = r.astype(np.uint8)
    rgba[:, :, 1] = g.astype(np.uint8)
    rgba[:, :, 2] = b.astype(np.uint8)
    rgba[:, :, 3] = (mask * 255).astype(np.uint8)

    img = Image.fromarray(rgba, 'RGBA')

    # ── 9. Soft blur pass on the gloss (keeps highlight from looking harsh) ───
    # We only blur the highlight layer, not the whole card.
    # Trick: blur the image slightly then mix a small amount back.
    blurred = img.filter(ImageFilter.GaussianBlur(radius=4))
    img     = Image.blend(img, blurred, alpha=0.18)

    return img


if __name__ == '__main__':
    print(f"Rendering bubble card {CARD_W}×{CARD_H}px …")
    bubble = make_bubble()
    bubble.save(OUT_PATH, 'PNG')
    print(f"✓ Saved → {OUT_PATH}")
    print(f"  Size : {CARD_W} × {CARD_H} px  |  Radius: {RADIUS} px")
    print(f"  Mode : RGBA  |  Colour base: Ship Cove #6D8CBA")
