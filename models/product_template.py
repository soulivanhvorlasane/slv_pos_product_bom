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
    
    pos_bom_ids = fields.One2many(
        'pos.product.bom',
        'product_tmpl_id',
        string='POS BoMs'
    )
    
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'is_pos_bom_product' in vals:
            for product in self:
                if product.is_pos_bom_product and not product.pos_bom_ids:
                    self.env['pos.product.bom'].sudo().create({
                        'product_tmpl_id': product.id,
                        'quantity': 1.0,
                        'uom_id': product.uom_id.id,
                    })
                elif not product.is_pos_bom_product and product.pos_bom_ids:
                    product.pos_bom_ids.sudo().unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductTemplate, self).create(vals_list)
        for product in products:
            if product.is_pos_bom_product and not product.pos_bom_ids:
                self.env['pos.product.bom'].sudo().create({
                    'product_tmpl_id': product.id,
                    'quantity': 1.0,
                    'uom_id': product.uom_id.id,
                })
        return products

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
