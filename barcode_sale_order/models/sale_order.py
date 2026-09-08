from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_scan_barcode(self, barcode):
        """Look up ``barcode`` and add/increment the matching product on this order.

        Reuses the standard ``sale.order.line`` create/write flow so that
        UoM, taxes, pricelist and description are computed exactly as they
        would be when a user adds the product manually (see
        ``sale.order.line`` precompute fields such as ``_compute_price_unit``
        and ``_compute_tax_ids``). No elevated privileges are used: normal
        ORM access rules apply to the calling user.

        :param str barcode: the scanned barcode.
        :return: dict with keys ``status`` ('ok'/'not_found'/'error'),
            ``message``, and on success ``product_name``, ``line_id``, ``qty``.
        """
        self.ensure_one()

        barcode = (barcode or '').strip()
        if not barcode:
            return {
                'status': 'error',
                'message': _("Please scan or enter a barcode."),
            }

        if self.state == 'cancel':
            return {
                'status': 'error',
                'message': _("This quotation is cancelled and cannot be modified."),
            }
        if self.locked:
            return {
                'status': 'error',
                'message': _("This order is locked and cannot be modified."),
            }

        product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
        if not product:
            return {
                'status': 'not_found',
                'message': _("Product not found for barcode: %s", barcode),
            }

        try:
            existing_line = self.order_line.filtered(
                lambda line: not line.display_type and line.product_id == product
            )[:1]
            if existing_line:
                new_qty = existing_line.product_uom_qty + 1
                existing_line.write({'product_uom_qty': new_qty})
                line = existing_line
            else:
                line = self.env['sale.order.line'].create({
                    'order_id': self.id,
                    'product_id': product.id,
                    'product_uom_qty': 1,
                })
                new_qty = line.product_uom_qty
        except UserError as exc:
            return {
                'status': 'error',
                'message': str(exc),
            }

        return {
            'status': 'ok',
            'message': _("%(product)s added.", product=product.display_name),
            'product_name': product.display_name,
            'line_id': line.id,
            'qty': new_qty,
        }
