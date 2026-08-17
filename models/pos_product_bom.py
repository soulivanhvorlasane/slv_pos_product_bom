from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class PosProductBom(models.Model):
    _name = 'pos.product.bom'
    _description = 'POS Product Bill of Materials'
    _order = 'name'

    name = fields.Char(
        string='Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New')
    )
    product_tmpl_id = fields.Many2one(
        'product.template', 
        string='Product', 
        required=True, 
        domain=[('is_pos_bom_product', '=', True)]
    )
    quantity = fields.Float(
        string='Quantity', 
        default=1.0, 
        required=True, 
        digits='Product Unit of Measure'
    )
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure', 
        required=True,
        domain="[('category_id', '=', product_tmpl_id_uom_category)]"
    )
    product_tmpl_id_uom_category = fields.Many2one(
        related='product_tmpl_id.uom_id.category_id',
        string='UoM Category'
    )
    bom_line_ids = fields.One2many(
        'pos.product.bom.line', 
        'bom_id', 
        string='BoM Lines'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
    ], string='Status', default='draft', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('pos.product.bom') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        for bom in self:
            if not bom.bom_line_ids:
                raise ValidationError(_("You cannot confirm a BoM without any ingredients."))
            if bom.quantity <= 0:
                raise ValidationError(_("BoM quantity must be strictly positive."))
            
            # Check for other confirmed BoMs for the same product template
            existing_confirmed_bom = self.search([
                ('product_tmpl_id', '=', bom.product_tmpl_id.id),
                ('state', '=', 'confirmed'),
                ('id', '!=', bom.id)
            ], limit=1)
            if existing_confirmed_bom:
                raise ValidationError(_("Only one confirmed BoM is allowed at a time for the product '%s'.") % bom.product_tmpl_id.display_name)
                
            bom.state = 'confirmed'
            
    def action_draft(self):
        for bom in self:
            bom.state = 'draft'

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.uom_id = self.product_tmpl_id.uom_id.id


class PosProductBomLine(models.Model):
    _name = 'pos.product.bom.line'
    _description = 'POS Product BoM Line'

    bom_id = fields.Many2one(
        'pos.product.bom', 
        string='BoM', 
        required=True, 
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Ingredient', 
        required=True
    )
    quantity = fields.Float(
        string='Quantity', 
        required=True, 
        digits='Product Unit of Measure'
    )
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure', 
        required=True,
        domain="[('category_id', '=', product_id_uom_category)]"
    )
    product_id_uom_category = fields.Many2one(
        related='product_id.uom_id.category_id',
        string='Ingredient UoM Category'
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
