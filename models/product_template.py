from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_pos_bom_product = fields.Boolean(
        string='Is POS BoM Product?',
        default=False,
        help='Check if this product has a Bill of Materials for POS.'
    )
    
    pos_bom_count = fields.Integer(
        string='POS BoM Count',
        compute='_compute_pos_bom_count'
    )

    def _compute_pos_bom_count(self):
        for template in self:
            template.pos_bom_count = self.env['pos.product.bom'].search_count([
                ('product_tmpl_id', '=', template.id)
            ])

    def action_view_pos_boms(self):
        self.ensure_one()
        return {
            'name': 'POS BoMs',
            'type': 'ir.actions.act_window',
            'res_model': 'pos.product.bom',
            'view_mode': 'list,form',
            'domain': [('product_tmpl_id', '=', self.id)],
            'context': {'default_product_tmpl_id': self.id},
        }
