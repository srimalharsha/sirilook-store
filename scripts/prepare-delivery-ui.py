from pathlib import Path

# The delivery calculation is maintained directly in index.html, product.html,
# and admin.html. Do not rewrite those files during deployment: doing so would
# deploy code different from the reviewed Git commit and could reintroduce bugs.
required = {
    "index.html": [
        "function cartDeliveryFee(items)",
        'const CART_KEY="sirilook_cart_v2";',
        "գෙවිය යුතු මුළු මුදල",
    ],
    "product.html": [
        'const key="sirilook_cart_v2";',
        "function styleDeliveryFee",
    ],
    "admin.html": [
        'id="freeDelivery"',
        "productDeliveryRangeRows",
    ],
}
for filename, markers in required.items():
    source = Path(filename).read_text(encoding="utf-8")
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise SystemExit(f"{filename}: required delivery code missing: {missing}")
    print(f"Delivery UI verified: {filename}")
