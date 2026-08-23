"""
One-off script to generate the app icon set for the PWA.
Draws a simple church/shield mark (no external assets, no emoji-font
dependency) at a few required sizes. Safe to delete after running once;
re-run any time to regenerate the icons.
"""
from PIL import Image, ImageDraw

GREEN = (42, 122, 75, 255)      # #2a7a4b
GREEN_DARK = (33, 97, 57, 255)  # #216139
WHITE = (255, 255, 255, 255)


def draw_mark(size):
    """Draws a rounded-square badge with a simple church silhouette
    (roof triangle + body + steeple cross) in the center, plus a small
    checkmark to nod at 'verified'."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    pad = int(size * 0.06)
    d.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=int(size * 0.22),
        fill=GREEN,
    )

    cx = size / 2
    body_w = size * 0.34
    body_h = size * 0.26
    body_top = size * 0.52
    body_bottom = body_top + body_h
    d.rectangle(
        [cx - body_w / 2, body_top, cx + body_w / 2, body_bottom],
        fill=WHITE,
    )

    roof_h = size * 0.16
    roof_top = body_top - roof_h
    d.polygon(
        [
            (cx - body_w / 2 - size * 0.03, body_top),
            (cx + body_w / 2 + size * 0.03, body_top),
            (cx, roof_top),
        ],
        fill=WHITE,
    )

    steeple_w = size * 0.045
    steeple_h = size * 0.14
    steeple_top = roof_top - steeple_h
    d.rectangle(
        [cx - steeple_w / 2, steeple_top, cx + steeple_w / 2, roof_top + size * 0.01],
        fill=WHITE,
    )
    arm_w = size * 0.10
    arm_h = size * 0.03
    arm_y = steeple_top + steeple_h * 0.32
    d.rectangle(
        [cx - arm_w / 2, arm_y, cx + arm_w / 2, arm_y + arm_h],
        fill=WHITE,
    )

    door_w = size * 0.09
    door_h = size * 0.12
    d.rounded_rectangle(
        [cx - door_w / 2, body_bottom - door_h, cx + door_w / 2, body_bottom],
        radius=int(door_w * 0.4),
        fill=GREEN_DARK,
    )

    return img


def save_flat(img, path):
    """Flatten onto white for contexts that don't support transparency well
    (apple-touch-icon should not be transparent)."""
    flat = Image.new("RGB", img.size, (255, 255, 255))
    flat.paste(img, mask=img.split()[3])
    flat.save(path)


if __name__ == "__main__":
    import os
    out_dir = os.path.join(os.path.dirname(__file__), "static", "icons")
    os.makedirs(out_dir, exist_ok=True)

    icon_512 = draw_mark(512)
    icon_512.save(os.path.join(out_dir, "icon-512.png"))

    icon_192 = draw_mark(192)
    icon_192.save(os.path.join(out_dir, "icon-192.png"))

    apple_touch = draw_mark(180)
    save_flat(apple_touch, os.path.join(out_dir, "apple-touch-icon.png"))

    favicon_sizes = [16, 32, 48]
    favicon_imgs = [draw_mark(s) for s in favicon_sizes]
    favicon_imgs[0].save(
        os.path.join(out_dir, "favicon.ico"),
        format="ICO",
        sizes=[(s, s) for s in favicon_sizes],
    )

    print("Icons written to", out_dir)
