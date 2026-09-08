from odoo import fields, models


class CommentsMixin(models.AbstractModel):
    _name = 'tree.comments.mixin'
    _description = 'Tree Comments Mixin'
    # Bundles mail.thread so any model that inherits this mixin gets
    # message_post/message_ids for free, even if it didn't already
    # inherit mail.thread on its own (e.g. sale.order.line does not).
    _inherit = ['mail.thread']

    comment_count = fields.Integer(
        string='Comments',
        compute='_compute_comment_count',
        store=False,
    )

    def _compute_comment_count(self):
        message_model = self.env['mail.message']
        for rec in self:
            rec.comment_count = message_model.search_count([
                ('res_id', '=', rec.id),
                ('model', '=', rec._name),
                ('message_type', 'in', ['comment', 'email']),
            ])
