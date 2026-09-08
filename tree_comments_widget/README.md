# Tree Comments Widget

A generic floating comments popup you can drop into any list view column —
see and post chatter comments for a row without opening its form view.

**Version:** 19.0.1.0.0
**License:** OPL-1 (Odoo Proprietary License v1.0) — required for paid listings on Odoo Apps
**Category:** Tools

## Features

- Reusable `comments_button` field widget usable on any list view, for any
  model.
- Shows a comment-count badge inline; click to open a floating popup
  positioned next to the row, with no page navigation.
- Loads and displays that record's `mail.message` comments (type `comment`
  or `email`).
- `@mention` autocomplete against `res.partner` users while typing.
- `Ctrl+Enter` (or `Cmd+Enter`) posts the comment; clicking outside the
  popup closes it.
- Posts through the standard `mail.thread.message_post` flow — no custom
  message storage, fully compatible with existing chatter/notifications.
- Drop-in `tree.comments.mixin` abstract model adds the `comment_count`
  field and bundles `mail.thread` itself — works on any model, even one
  without chatter today (e.g. `sale.order.line`).

## Installation

1. Copy the `tree_comments_widget` folder into an addons path visible to
   your Odoo 19 instance.
2. Update the apps list (Apps > Update Apps List).
3. Search for "Tree Comments Widget" and install it.

The module only depends on the standard `mail` app.

## Configuration

This module ships no standalone UI of its own — it's a building block for
other modules/views. To use it on a model:

1. Add `tree.comments.mixin` to that model's `_inherit` list. The mixin
   bundles `mail.thread` itself, so this works even on models that don't
   have chatter today (e.g. `sale.order.line`, which has no `mail.thread`
   of its own in Odoo core) — no separate step needed.
2. In the list view XML, add the `comment_count` field with
   `widget="comments_button"`.

See `static/description/index.html` for the full step-by-step guide with
code samples.

## Usage

1. Open any list view where a developer has added the comments column.
2. Click the comments icon on a row to open the floating popup.
3. Read existing comments, type a new one (use `@` to mention a user), and
   press Ctrl+Enter or click Comment.
4. The badge count updates immediately after posting.

## Known Limitations (v1)

- The popup shows plain-text stripped comments only (HTML formatting from
  rich-text chatter messages is not rendered, only its text content).
- No support yet for attachments/images within the popup's comment
  composer — text-only posting.

## Screenshots

Illustrative mockups are under `static/description/` (icon, banner) and
the interactive demo built into `index.html`'s "How It Looks" section
(rendered directly as part of the module guide, not a static image).

## Publishing on Odoo Apps (checklist)

1. **License**: already set to `OPL-1` in the manifest — mandatory for a
   paid listing (LGPL/free licenses cannot be sold).
2. **`LICENSE`** file with the OPL-1 terms is included at the module root.
3. `author` is "MD ERP Solutions" and `support` is `mrdudedeg@gmail.com`
   in `__manifest__.py`.
4. **Suggested price: $29.00 (one-time)** — shown as a badge in
   `index.html`. There is no `price` key in the Odoo manifest format;
   actual billing is configured on the module's listing page on
   apps.odoo.com after upload/submission.
5. Run a manual smoke test on a clean database before submitting: install
   the module, add the mixin + widget to a test model's list view, confirm
   posting and the count badge both work.
6. Odoo Apps reviews submissions manually — expect a review cycle before
   the listing goes live.

## Demo Data

No demo data is shipped — this module has no UI of its own until another
model opts into the mixin and widget.

## Support

For issues or feature requests, contact **mrdudedeg@gmail.com**.
