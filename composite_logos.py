#!/usr/bin/env python3
"""
composite_logos.py — Logo compositing for Dr Liew social media images
Orthopaedics 360 / drchienwenliew.com.au

Loads an AI-generated image, applies a visual template (gradient overlay,
typography, design panels), draws the Ship Cove (#6D8CBA) brand bar, then
composites real PNG logos and (for Facebook) a circular headshot.

TEMPLATES
─────────
  authority  : Dark editorial — full-bleed dark scene, large bold white headline
               in upper zone, Ship Cove accent line, minimal powerful layout.
  editorial  : Magazine feature — cinematic scene upper 62%, Alabaster panel
               lower 38% with bold dark headline + supporting text.
  pullquote  : Full-bleed cinematic scene, gradient fade at bottom third,
               large white quote text over gradient.
  scene      : Clean scene, brand bar only (original behaviour). Default.

PLATFORM SPECS
──────────────
  instagram : (DR) LIEW wordmark only
  linkedin  : (DR) LIEW wordmark + Orthopaedics 360 logo
  facebook  : Circular headshot + Orthopaedics 360 logo + (DR) LIEW wordmark

Usage:
  python3 composite_logos.py <input> <platform> <output> [template] [headline] [subtext]

Examples:
  python3 composite_logos.py bg.jpg instagram out.jpg scene
  python3 composite_logos.py bg.jpg instagram out.jpg authority "Your hip pain has a solution" "Dr Chien-Wen Liew — Orthopaedic Surgeon"
  python3 composite_logos.py bg.jpg linkedin out.jpg pullquote "92% of patients return to full activity within 6 months"
  python3 composite_logos.py bg.jpg instagram out.jpg editorial "5 Signs You Need Hip Replacement" "Swipe to learn the key indicators"
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops
import urllib.request
from io import BytesIO

# ── Asset paths ────────────────────────────────────────────────────────────────
ASSETS_DIR    = '/Users/cwl/Desktop/Claude Missions/Dr Liew Social Media'
WORDMARK_PATH = os.path.join(ASSETS_DIR, 'logo-drliew-wordmark.png')
ORTHO360_PATH = os.path.join(ASSETS_DIR, 'logo-orthopaedics360.png')
HEADSHOT_PATH = os.path.join(ASSETS_DIR, 'Liew headshot.jpg')

FONT_BOLD    = os.path.join(ASSETS_DIR, 'Poppins-Bold.ttf')
FONT_REGULAR = os.path.join(ASSETS_DIR, 'Poppins-Regular.ttf')
FONT_LIGHT   = os.path.join(ASSETS_DIR, 'Poppins-Light.ttf')
FONT_BLACK   = os.path.join(ASSETS_DIR, 'Lato-Black.ttf')

# ── Brand colours ──────────────────────────────────────────────────────────────
SHIP_COVE = (109, 140, 186)    # #6D8CBA — primary brand blue
DARK_NAVY = (27,  37,  53)     # #1B2535 — deep authority dark
MID_NAVY  = (43,  58,  78)     # #2B3A4E — mid brand dark
ALABASTER = (248, 248, 248)    # #F8F8F8 — light background
WHITE     = (255, 255, 255)
OFF_WHITE = (240, 242, 245)    # warm white for text on dark
WARM_GRAY = (160, 165, 172)    # supporting text on dark

# ── Platform specifications ────────────────────────────────────────────────────
PLATFORM_SPECS = {
    'instagram': {
        'size':            (1080, 1350),
        'bar_h':           108,
        'wordmark_w':      260,
        'wm_align':        'left',
        'wm_margin':       48,
        'ortho360':        False,
        'headshot':        False,
        'auto_fill_strip': True,
        'fill_color':      DARK_NAVY,
    },
    'linkedin': {
        'size':       (1920, 1080),
        'bar_h':      88,
        'wordmark_w': 230,
        'wm_align':   'right',
        'wm_margin':  52,
        'ortho360':   True,
        'ortho360_w': 190,
        'headshot':   False,
    },
    'facebook': {
        'size':            (1080, 1080),
        'bar_h':           145,
        'wordmark_w':      200,
        'wm_align':        'right',
        'wm_margin':       44,
        'ortho360':        True,
        'ortho360_w':      155,
        'headshot':        True,
        'headshot_d':      122,
        'headshot_cx':     70,
        'headshot_in_bar': True,
    },
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def load_image(path_or_url: str) -> Image.Image:
    if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
        with urllib.request.urlopen(path_or_url) as resp:
            return Image.open(BytesIO(resp.read())).copy()
    return Image.open(path_or_url)


def resize_and_crop(img: Image.Image, W: int, H: int) -> Image.Image:
    bw, bh = img.size
    scale  = max(W / bw, H / bh)
    new_bw = int(bw * scale)
    new_bh = int(bh * scale)
    img    = img.resize((new_bw, new_bh), Image.LANCZOS)
    left   = (new_bw - W) // 2
    top    = (new_bh - H) // 2
    return img.crop((left, top, left + W, top + H))


def resize_logo(logo: Image.Image, target_width: int) -> Image.Image:
    aspect = logo.size[1] / logo.size[0]
    return logo.resize((target_width, max(1, int(target_width * aspect))), Image.LANCZOS)


def tint_to_white(logo: Image.Image) -> Image.Image:
    logo = logo.convert('RGBA')
    r, g, b, a = logo.split()
    white_ch = Image.new('L', logo.size, 255)
    return Image.merge('RGBA', (white_ch, white_ch, white_ch, a))


def make_circle(img: Image.Image, diameter: int,
                border_color=WHITE, border_px: int = 4) -> Image.Image:
    img  = img.convert('RGBA')
    w, h = img.size
    side = min(w, h)
    cx   = (w - side) // 2
    cy   = max(0, int((h - side) * 0.22))
    img  = img.crop((cx, cy, cx + side, cy + side))
    img  = img.resize((diameter, diameter), Image.LANCZOS)
    mask = Image.new('L', (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    circle = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    circle.paste(img, mask=mask)
    if border_px <= 0:
        return circle
    total     = diameter + border_px * 2
    bordered  = Image.new('RGBA', (total, total), (0, 0, 0, 0))
    ring_mask = Image.new('L', (total, total), 0)
    ImageDraw.Draw(ring_mask).ellipse((0, 0, total - 1, total - 1), fill=255)
    ring = Image.new('RGBA', (total, total), border_color + (255,))
    ring.putalpha(ring_mask)
    bordered.paste(ring, (0, 0), ring)
    bordered.paste(circle, (border_px, border_px), circle)
    return bordered


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text: str, font: ImageFont.FreeTypeFont,
              max_width: int, draw: ImageDraw.Draw) -> list:
    words  = text.split()
    lines  = []
    line   = ''
    for word in words:
        test = f'{line} {word}'.strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and line:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


def draw_text_shadowed(draw: ImageDraw.Draw, pos: tuple, text: str,
                       font: ImageFont.FreeTypeFont, fill: tuple,
                       shadow_offset: int = 3) -> None:
    sx, sy = pos[0] + shadow_offset, pos[1] + shadow_offset
    draw.text((sx, sy), text, font=font, fill=(0, 0, 0, 100))
    draw.text(pos, text, font=font, fill=fill)


def build_vertical_gradient(W: int, H: int,
                             top_color: tuple, top_alpha: int,
                             bot_color: tuple, bot_alpha: int,
                             y_start: int, y_end: int) -> Image.Image:
    """Return an RGBA Image of size (W,H) with a vertical gradient band."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pix = img.load()
    band_h = y_end - y_start
    for y in range(y_start, y_end):
        t = (y - y_start) / max(band_h - 1, 1)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
        a = int(top_alpha  + (bot_alpha  - top_alpha)  * t)
        for x in range(W):
            pix[x, y] = (r, g, b, a)
    return img


# ── Template overlays ──────────────────────────────────────────────────────────

def apply_authority_overlay(base: Image.Image, W: int, H: int, bar_top: int,
                             headline: str, subtext: str) -> Image.Image:
    """
    AUTHORITY: top-to-centre dark vignette, large bold white headline centred
    in upper 50%, Ship Cove accent line, light subtext beneath.
    """
    # Dark vignette gradient — top is opaque dark, fades to transparent by 58%
    vignette = build_vertical_gradient(
        W, H,
        top_color=DARK_NAVY, top_alpha=200,
        bot_color=DARK_NAVY, bot_alpha=0,
        y_start=0, y_end=int(H * 0.58)
    )
    base = base.convert('RGBA')
    base = Image.alpha_composite(base, vignette)

    draw = ImageDraw.Draw(base)

    text_zone_top = int(H * 0.07)
    text_zone_bot = int(H * 0.52)
    text_zone_h   = text_zone_bot - text_zone_top
    text_w        = int(W * 0.80)

    # Auto-size headline
    font_size = 108
    while font_size > 40:
        font   = load_font(FONT_BLACK, font_size)
        lines  = wrap_text(headline, font, text_w, draw)
        line_h = draw.textbbox((0, 0), 'Ag', font=font)[3] + 14
        if line_h * len(lines) <= text_zone_h * 0.72:
            break
        font_size -= 5

    font      = load_font(FONT_BLACK, font_size)
    lines     = wrap_text(headline, font, text_w, draw)
    line_h    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 14
    total_txt = line_h * len(lines)
    y_start   = text_zone_top + (text_zone_h - total_txt) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        lw   = bbox[2] - bbox[0]
        x    = (W - lw) // 2
        draw_text_shadowed(draw, (x, y_start + i * line_h), line, font,
                           WHITE + (255,), shadow_offset=4)

    print(f'  ✓ Authority headline — {len(lines)} lines @ {font_size}pt')

    # Ship Cove accent line
    accent_y = y_start + total_txt + 22
    line_len  = min(int(W * 0.32), 350)
    lx        = (W - line_len) // 2
    draw.rectangle([(lx, accent_y), (lx + line_len, accent_y + 5)],
                   fill=SHIP_COVE + (255,))

    if subtext:
        sub_font  = load_font(FONT_LIGHT, 36)
        sub_lines = wrap_text(subtext, sub_font, text_w, draw)
        sy = accent_y + 26
        for sline in sub_lines:
            bbox = draw.textbbox((0, 0), sline, font=sub_font)
            sx   = (W - (bbox[2] - bbox[0])) // 2
            draw.text((sx, sy), sline, font=sub_font, fill=OFF_WHITE + (200,))
            sy += 48

    return base


def apply_editorial_overlay(base: Image.Image, W: int, H: int, bar_top: int,
                             headline: str, subtext: str) -> Image.Image:
    """
    EDITORIAL: Alabaster panel in lower 38%, bold dark-navy headline,
    Ship Cove left-border accent, gray subtext.
    """
    panel_top = int(H * 0.62)
    panel_bot = bar_top

    base = base.convert('RGBA')
    draw = ImageDraw.Draw(base)

    # Alabaster panel
    draw.rectangle([(0, panel_top), (W, panel_bot)], fill=ALABASTER + (250,))

    # Ship Cove left accent bar
    draw.rectangle([(0, panel_top), (7, panel_bot)], fill=SHIP_COVE + (255,))

    # Thin top rule
    draw.rectangle([(0, panel_top), (W, panel_top + 4)], fill=SHIP_COVE + (180,))

    pad_x     = 58
    pad_y     = 32
    text_w    = W - pad_x * 2
    available = (panel_bot - panel_top) - pad_y * 2 - 90

    # Auto-size headline
    font_size = 72
    while font_size > 30:
        font  = load_font(FONT_BOLD, font_size)
        lines = wrap_text(headline, font, text_w, draw)
        lh    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 10
        if lh * len(lines) <= available:
            break
        font_size -= 4

    font  = load_font(FONT_BOLD, font_size)
    lines = wrap_text(headline, font, text_w, draw)
    lh    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 10
    y     = panel_top + pad_y

    for line in lines:
        draw.text((pad_x, y), line, font=font, fill=MID_NAVY + (255,))
        y += lh

    print(f'  ✓ Editorial headline — {len(lines)} lines @ {font_size}pt')

    if subtext:
        sub_font  = load_font(FONT_REGULAR, 34)
        sub_lines = wrap_text(subtext, sub_font, text_w - 10, draw)
        y += 8
        for sline in sub_lines:
            draw.text((pad_x, y), sline, font=sub_font, fill=WARM_GRAY + (255,))
            y += 44

    return base


def draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int,
                      fill: tuple) -> None:
    """Draw a filled rounded rectangle using overlapping rectangles + corner ellipses."""
    x0, y0, x1, y1 = xy
    # Clamp radius so it never exceeds half the width or height
    r = max(0, min(radius, (x1 - x0) // 2, (y1 - y0) // 2))
    if r == 0:
        draw.rectangle([x0, y0, x1, y1], fill=fill)
        return
    # Three rectangles (cross)
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    # Four corner ellipses
    draw.ellipse([x0,      y0,      x0 + r*2, y0 + r*2], fill=fill)
    draw.ellipse([x1 - r*2, y0,     x1,       y0 + r*2], fill=fill)
    draw.ellipse([x0,      y1 - r*2, x0 + r*2, y1],      fill=fill)
    draw.ellipse([x1 - r*2, y1 - r*2, x1,      y1],      fill=fill)


def apply_info_overlay(base: Image.Image, W: int, H: int, bar_top: int,
                       headline: str, bullets_raw: str) -> Image.Image:
    """
    INFO: Educational content card template.
    - Photo occupies top ~52% of image (hard cut — no fade)
    - #A2B9D8 (Ship Cove Light) panel below photo
    - 3D glossy Ship Cove blue bubble card with drop shadow:
        - White gradient sheen over top 44% (classic 3D pill effect)
        - White bold headline
        - White bullet points
        - White URL at bottom
    Usage: bullets_raw is pipe-separated facts, e.g.
        "Fact one here|Fact two here|Fact three here"
    """
    SHIP_COVE_LIGHT_RGB = (162, 185, 216)   # #A2B9D8 — panel background
    URL_TEXT            = "drchienwenliew.com.au"
    CARD_RADIUS         = 22      # corner radius — larger = rounder pill
    SHADOW_OFFSET       = 9       # drop-shadow offset in px
    SHADOW_COLOR        = (30, 50, 80, 140)   # deep navy shadow

    base = base.convert('RGBA')

    # ── 1. Hard cut between photo (top 52%) and light-blue panel ────────────
    photo_h = int(H * 0.52)
    panel_y = photo_h

    panel_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(panel_layer).rectangle(
        [(0, panel_y), (W, H)], fill=SHIP_COVE_LIGHT_RGB + (255,))
    base = Image.alpha_composite(base, panel_layer)

    # ── 2. Card geometry ─────────────────────────────────────────────────────
    card_margin = int(W * 0.055)   # ~59px each side @ 1080px
    card_top    = panel_y + 22
    card_bot    = bar_top - 16
    card_left   = card_margin
    card_right  = W - card_margin
    card_h      = card_bot - card_top
    card_w      = card_right - card_left

    # ── 3. Drop shadow (soft dark rect behind card) ──────────────────────────
    shadow_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_rounded_rect(
        ImageDraw.Draw(shadow_layer),
        (card_left + SHADOW_OFFSET, card_top + SHADOW_OFFSET,
         card_right + SHADOW_OFFSET, card_bot + SHADOW_OFFSET),
        CARD_RADIUS, SHADOW_COLOR,
    )
    base = Image.alpha_composite(base, shadow_layer)

    # ── 4. Pre-rendered 3D bubble card asset ─────────────────────────────────
    bubble_path = os.path.join(os.path.dirname(__file__), 'bubble_card_instagram.png')
    if os.path.exists(bubble_path):
        bubble = Image.open(bubble_path).convert('RGBA')
        # Scale to actual card size if geometry differs
        if bubble.size != (card_w, card_h):
            bubble = bubble.resize((card_w, card_h), Image.LANCZOS)
        card_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        card_layer.paste(bubble, (card_left, card_top), bubble)
        base = Image.alpha_composite(base, card_layer)
        print(f"  ✓ Bubble asset loaded ({card_w}×{card_h}px)")
    else:
        # Fallback: flat Ship Cove card if asset missing
        card_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw_rounded_rect(
            ImageDraw.Draw(card_layer),
            (card_left, card_top, card_right, card_bot),
            CARD_RADIUS, SHIP_COVE + (255,),
        )
        base = Image.alpha_composite(base, card_layer)
        print(f"  ⚠ bubble_card_instagram.png not found — using flat fallback")

    draw = ImageDraw.Draw(base)

    # ── 7. Text layout (all white on Ship Cove blue) ─────────────────────────
    inner_x  = card_left + 36   # left text margin
    inner_y  = card_top  + 22
    text_w   = card_right - inner_x - 28

    bullets   = [b.strip() for b in bullets_raw.split('|') if b.strip()]
    n_bullets = len(bullets)

    # URL zone anchored to card bottom
    url_font = load_font(FONT_LIGHT, 24)
    url_h    = 32
    url_y    = card_bot - url_h - 6

    # Headline auto-size (~28% of card height)
    hl_budget = int(card_h * 0.28)
    font_size = 52
    while font_size > 22:
        font  = load_font(FONT_BOLD, font_size)
        lines = wrap_text(headline, font, text_w, draw)
        lh    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 8
        if lh * len(lines) <= hl_budget:
            break
        font_size -= 2

    font  = load_font(FONT_BOLD, font_size)
    lines = wrap_text(headline, font, text_w, draw)
    lh    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 8
    for line in lines:
        draw.text((inner_x, inner_y), line, font=font, fill=WHITE + (255,))
        inner_y += lh

    # Thin white divider under headline
    inner_y += 6
    draw.rectangle(
        [(inner_x, inner_y), (inner_x + int(text_w * 0.40), inner_y + 2)],
        fill=(255, 255, 255, 130))
    inner_y += 10

    # Bullets — auto-size to fill space between headline and URL
    bullet_zone = url_y - 8 - inner_y
    bfont_size  = 28
    while bfont_size > 13:
        bfont = load_font(FONT_REGULAR, bfont_size)
        blh   = draw.textbbox((0, 0), 'Ag', font=bfont)[3] + 8
        if blh * n_bullets * 1.5 <= bullet_zone:
            break
        bfont_size -= 1

    bfont    = load_font(FONT_REGULAR, bfont_size)
    dot_font = load_font(FONT_BOLD, bfont_size)
    blh      = draw.textbbox((0, 0), 'Ag', font=bfont)[3] + 8
    dot_w    = draw.textbbox((0, 0), '• ', font=dot_font)[2]
    btext_w  = text_w - dot_w - 4

    for bullet in bullets:
        blines = wrap_text(bullet, bfont, btext_w, draw)
        for li, bl in enumerate(blines):
            if inner_y + blh > url_y - 6:
                break
            if li == 0:
                draw.text((inner_x, inner_y), '•', font=dot_font,
                          fill=(255, 255, 255, 200))
                bx = inner_x + dot_w + 2
            else:
                bx = inner_x + dot_w + 2
            draw.text((bx, inner_y), bl, font=bfont,
                      fill=(255, 255, 255, 230))
            inner_y += blh
        else:
            continue
        break

    # URL — white, 65% opacity, bottom of card
    draw.text((inner_x, url_y), URL_TEXT, font=url_font,
              fill=(255, 255, 255, 165))

    print(f'  ✓ Info card (3D gloss) — headline {len(lines)} lines @ {font_size}pt, '
          f'{n_bullets} bullets @ {bfont_size}pt')

    return base


def apply_pullquote_overlay(base: Image.Image, W: int, H: int, bar_top: int,
                             headline: str, subtext: str) -> Image.Image:
    """
    PULL QUOTE: gradient fade from transparent → deep navy over lower 45%,
    large white bold quote text in gradient zone.
    """
    grad_top = int(H * 0.44)
    grad_bot = bar_top

    # Gradient: transparent at top → solid dark navy at bottom
    gradient = build_vertical_gradient(
        W, H,
        top_color=DARK_NAVY, top_alpha=0,
        bot_color=DARK_NAVY, bot_alpha=235,
        y_start=grad_top, y_end=grad_bot
    )
    base = base.convert('RGBA')
    base = Image.alpha_composite(base, gradient)

    draw = ImageDraw.Draw(base)

    # Decorative opening quote mark
    q_font = load_font(FONT_BLACK, 160)
    draw.text((50, grad_top - 30), '“', font=q_font,
              fill=SHIP_COVE + (180,))

    # Quote text zone
    text_zone_top = grad_top + int((grad_bot - grad_top) * 0.20)
    text_zone_h   = grad_bot - text_zone_top - 50
    text_w        = int(W * 0.84)
    margin_x      = (W - text_w) // 2

    font_size = 76
    while font_size > 32:
        font   = load_font(FONT_BOLD, font_size)
        lines  = wrap_text(headline, font, text_w, draw)
        line_h = draw.textbbox((0, 0), 'Ag', font=font)[3] + 14
        if line_h * len(lines) <= text_zone_h - 60:
            break
        font_size -= 4

    font      = load_font(FONT_BOLD, font_size)
    lines     = wrap_text(headline, font, text_w, draw)
    line_h    = draw.textbbox((0, 0), 'Ag', font=font)[3] + 14
    total_txt = line_h * len(lines)
    y_start   = text_zone_top + max(0, (text_zone_h - total_txt - 50) // 2)

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        lw   = bbox[2] - bbox[0]
        x    = (W - lw) // 2
        draw_text_shadowed(draw, (x, y_start + i * line_h), line, font,
                           WHITE + (255,), shadow_offset=3)

    print(f'  ✓ Pull quote — {len(lines)} lines @ {font_size}pt')

    if subtext:
        sub_font = load_font(FONT_LIGHT, 36)
        sub_y    = y_start + total_txt + 20
        # Short accent dash before attribution
        draw.rectangle([(margin_x, sub_y + 22), (margin_x + 40, sub_y + 25)],
                       fill=SHIP_COVE + (255,))
        draw.text((margin_x + 56, sub_y + 8), subtext, font=sub_font,
                  fill=WARM_GRAY + (230,))

    return base


# ── Main compositing function ──────────────────────────────────────────────────

def composite_logos(input_path: str, platform: str, output_path: str,
                    template: str = 'scene',
                    headline: str = '', subtext: str = '') -> None:

    if platform not in PLATFORM_SPECS:
        raise ValueError(f"Unknown platform '{platform}'. "
                         "Use: instagram | linkedin | facebook")

    spec    = PLATFORM_SPECS[platform]
    W, H    = spec['size']
    bar_h   = spec['bar_h']
    bar_top = H - bar_h

    print(f"\n── Compositing logos ───────────────────────────")
    print(f"  Platform : {platform}  |  Template: {template}")
    print(f"  Output   : {output_path}")

    # ── 1. Load & resize base image ────────────────────────────────────────────
    print(f"  Loading  : {input_path[:80]}...")
    base = load_image(input_path).convert('RGBA')
    base = resize_and_crop(base, W, H)

    # ── 2. Apply visual template overlay ──────────────────────────────────────
    if template == 'authority' and headline:
        base = apply_authority_overlay(base, W, H, bar_top, headline, subtext)
    elif template == 'editorial' and headline:
        base = apply_editorial_overlay(base, W, H, bar_top, headline, subtext)
    elif template == 'pullquote' and headline:
        base = apply_pullquote_overlay(base, W, H, bar_top, headline, subtext)
    elif template == 'info' and headline:
        # subtext carries the pipe-separated bullet points for the info template
        base = apply_info_overlay(base, W, H, bar_top, headline, subtext)

    # ── 3. Auto-fill large Alabaster strip above bar (scene mode only) ─────────
    draw = ImageDraw.Draw(base)
    if spec.get('auto_fill_strip') and template == 'scene':
        fill_color  = spec['fill_color']
        strip_start = bar_top
        sample_x    = W // 2
        for y in range(bar_top - 1, max(bar_top - 600, 0), -1):
            px = base.getpixel((sample_x, y))
            r, g, b = px[0], px[1], px[2]
            if not (r > 220 and g > 220 and b > 220):
                strip_start = y + 1
                break
        strip_h = bar_top - strip_start
        if strip_start < bar_top and strip_h > 280:
            draw.rectangle([(0, strip_start), (W, bar_top)],
                           fill=fill_color + (255,))
            print(f"  ✓ Auto-fill strip → y={strip_start}–{bar_top} ({strip_h}px)")
        else:
            print(f"  · Auto-fill strip skipped ({strip_h}px)")

    # ── 4. Draw Ship Cove brand bar ────────────────────────────────────────────
    draw = ImageDraw.Draw(base)
    draw.rectangle([(0, bar_top), (W, H)], fill=SHIP_COVE + (255,))
    print(f"  ✓ Brand bar → #6D8CBA, {bar_h}px, y={bar_top}–{H}")

    # ── 5. Circular headshot — Facebook only ───────────────────────────────────
    headshot_right = 0
    if spec.get('headshot'):
        hs     = Image.open(HEADSHOT_PATH)
        d      = spec['headshot_d']
        circle = make_circle(hs, d, border_color=WHITE, border_px=4)
        cw, ch = circle.size
        cx      = spec['headshot_cx']
        paste_x = cx - cw // 2
        paste_y = bar_top + 8 if spec.get('headshot_in_bar') else bar_top - ch // 2
        base.paste(circle, (paste_x, paste_y), circle)
        headshot_right = paste_x + cw
        print(f"  ✓ Headshot → ({paste_x},{paste_y}), ⌀{d}px")

    # ── 6. Orthopaedics 360 logo ───────────────────────────────────────────────
    if spec.get('ortho360'):
        ortho = Image.open(ORTHO360_PATH).convert('RGBA')
        ortho = tint_to_white(ortho)
        ortho = resize_logo(ortho, spec['ortho360_w'])
        ow, oh = ortho.size
        if spec.get('headshot'):
            ox = headshot_right + 18
        else:
            ox = W - spec['wordmark_w'] - spec['wm_margin'] - ow - 32
        oy = bar_top + (bar_h - oh) // 2
        base.paste(ortho, (ox, oy), ortho)
        print(f"  ✓ Ortho360 → ({ox},{oy}), {ow}×{oh}px")

    # ── 7. (DR) LIEW wordmark ─────────────────────────────────────────────────
    wordmark = Image.open(WORDMARK_PATH).convert('RGBA')
    wordmark = tint_to_white(wordmark)
    wordmark = resize_logo(wordmark, spec['wordmark_w'])
    wm_w, wm_h = wordmark.size
    margin = spec['wm_margin']
    wx     = (W - wm_w - margin) if spec['wm_align'] == 'right' else margin
    wy     = bar_top + (bar_h - wm_h) // 2
    base.paste(wordmark, (wx, wy), wordmark)
    print(f"  ✓ Wordmark → ({wx},{wy}), {wm_w}×{wm_h}px, align={spec['wm_align']}")

    # ── 8. Save ────────────────────────────────────────────────────────────────
    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else '.',
        exist_ok=True)
    base.convert('RGB').save(output_path, 'JPEG', quality=95, optimize=True)
    print(f"  ✓ Saved → {output_path}  ({W}×{H}px)")
    print(f"── Done ─────────────────────────────────────────\n")


# ── CLI entry point ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    input_path  = sys.argv[1]
    platform    = sys.argv[2]
    output_path = sys.argv[3]
    template    = sys.argv[4] if len(sys.argv) > 4 else 'scene'
    headline    = sys.argv[5] if len(sys.argv) > 5 else ''
    subtext     = sys.argv[6] if len(sys.argv) > 6 else ''

    composite_logos(input_path, platform, output_path, template, headline, subtext)
