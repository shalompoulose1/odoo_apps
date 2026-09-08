# Barcode Scanning for Sale Orders

Scan product barcodes directly on a Sale Order to add products or increment
existing line quantities — no manual product search required.

**Version:** 19.0.1.0.0
**License:** OPL-1 (Odoo Proprietary License v1.0) — required for paid listings on Odoo Apps
**Category:** Sales/Sales

## Features

- "Start Barcode Scanning" toggle embedded in the Sale Order form, above the
  order lines.
- Works with standard USB/keyboard-wedge barcode scanners out of the box —
  reuses Odoo's core `barcode` service, so it does not interfere with normal
  keyboard input on other fields.
- Optional camera-based scanning on supported browsers/devices (reuses
  Odoo's built-in camera barcode scanner — no third-party JS library added).
- Scanning a barcode already on the order increases that line's quantity by
  1; scanning a new barcode adds a new order line.
- Product lookup is variant-aware (`product.product.barcode`), skips
  archived products, and reports a clear warning for unknown barcodes
  without creating an empty line.
- Pricing, taxes, UoM and description are computed by the standard
  `sale.order.line` business logic (pricelist, fiscal position, customer,
  currency) — scanning behaves like adding the product manually.
- Respects existing Sale Order access rights; no elevated (`sudo`) access is
  used anywhere.
- Scanning is blocked once the order is confirmed and locked, or cancelled,
  matching standard Sale Order editability rules.
- Rapid, back-to-back scans are queued and processed in order so nothing is
  lost during fast scanning sessions.

## Installation

1. Copy the `barcode_sale_order` folder into an addons path visible to your
   Odoo 19 instance.
2. Update the apps list (Apps > Update Apps List).
3. Search for "Barcode Scanning for Sale Orders" and install it.

No additional configuration or external dependencies are required. The
module depends on the standard `sale` and `barcodes` apps only.

## Configuration

No configuration screen is needed. Ensure the products you intend to scan
have a `Barcode` set on the specific **product variant** (Sales/Inventory
tab of the product form).

## Usage

1. Open an existing Sale Order (must be saved — Draft or Quotation Sent).
2. Click **Start Barcode Scanning**, above the Order Lines tab.
3. Scan a product barcode with a USB scanner, or use the camera button if
   shown on your device.
4. The product is added as a new order line, or its quantity is increased
   by 1 if it is already on the order.
5. If a barcode does not match any product, a warning notification is
   shown and scanning can continue immediately.
6. Click **Stop Barcode Scanning** when done, then confirm the order as
   usual.

## Known Limitations (v1)

- If the same product appears on the order in more than one line (e.g. two
  lines with different manually-set Units of Measure), scanning increments
  only the first matching line.
- Barcode-to-product matching is a direct, exact match on
  `product.product.barcode` — GS1 barcode parsing (embedded quantity,
  weight, lot/serial number segments) is not implemented in v1.
- Camera scanning availability depends on browser/device support for the
  underlying barcode detection API used by Odoo core; on unsupported
  browsers only the USB scanner input works.
- There is no persisted scan history/log in v1 (by design, to avoid adding
  an unnecessary model).

## Screenshots

Illustrative mockups are included under `static/description/` for the
Apps store listing:
- `scan_panel_inactive.png` — scanner panel, inactive state
- `scan_panel_active.png` — scanner panel, active state with last scan info
- `order_line_added.png` — order line added after a scan

These are generated mockups of the actual panel layout, not live captures
of a running instance — swap them for real screenshots taken from your own
Odoo instance before submitting to the store, since marketplaces generally
expect genuine product screenshots.

## Publishing on Odoo Apps (checklist)

1. **License**: already set to `OPL-1` in the manifest — mandatory for a
   paid listing (LGPL/free licenses cannot be sold).
2. **`LICENSE`** file with the OPL-1 terms is included at the module root.
3. `author` is "MD ERP Solutions" and `support` is `mrdudedeg@gmail.com` in
   `__manifest__.py` — update these if either changes. No `website` key is
   set (optional field; add one later if you set up a site).
4. Replace the mockup screenshots with real captures from a running
   instance before submitting (icon/banner are final; see Screenshots
   section above).
5. **Suggested price: $49.00 (one-time)** — shown on the `index.html`
   listing page as informational copy. There is no `price` key in the
   Odoo manifest format; actual billing is configured on the module's
   listing page on apps.odoo.com after upload/submission.
6. Run the full test suite against a clean database before submitting
   (`-i barcode_sale_order --test-enable --stop-after-init`).
7. Odoo Apps reviews submissions manually — expect a review cycle before
   the listing goes live.

## Demo Data

No demo data is shipped. To try the module manually, create or use any
Sale Order, set a barcode on a product variant, and follow the Usage steps
above.

## Support

For issues or feature requests, contact **mrdudedeg@gmail.com**.
