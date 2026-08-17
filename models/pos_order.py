from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_move_from_pos_order_lines(self, lines):
        # Identify lines that have a confirmed POS BoM
        bom_lines = self.env['pos.order.line']
        normal_lines = self.env['pos.order.line']
        
        bom_cache = {}
        for line in lines:
            if line.product_id.is_pos_bom_product:
                tmpl_id = line.product_id.product_tmpl_id.id
                if tmpl_id not in bom_cache:
                    bom_cache[tmpl_id] = self.env['pos.product.bom'].search([
                        ('product_tmpl_id', '=', tmpl_id),
                        ('state', '=', 'confirmed')
                    ], limit=1)
                
                if bom_cache[tmpl_id]:
                    bom_lines |= line
                else:
                    normal_lines |= line
            else:
                normal_lines |= line

        # Call super for normal lines to handle them standardly
        if normal_lines:
            super()._create_move_from_pos_order_lines(normal_lines)

        # Handle BoM lines
        if bom_lines:
            move_vals = []
            for line in bom_lines:
                bom = bom_cache[line.product_id.product_tmpl_id.id]
                for component in bom.bom_line_ids:
                    # Required Qty = (Ingredient Qty / BoM Header Qty) * Order Line Qty
                    required_qty = (component.quantity / bom.quantity) * abs(line.qty)
                    
                    # Convert UoM to the product's default UoM if needed
                    if component.uom_id != component.product_id.uom_id:
                        required_qty = component.uom_id._compute_quantity(
                            required_qty, 
                            component.product_id.uom_id, 
                            rounding_method='HALF-UP'
                        )
                    
                    # Prepare stock move values
                    move_vals.append({
                        'name': f"{line.name} ({component.product_id.display_name})",
                        'product_uom': component.product_id.uom_id.id,
                        'picking_id': self.id,
                        'picking_type_id': self.picking_type_id.id,
                        'product_id': component.product_id.id,
                        'product_uom_qty': required_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'company_id': self.company_id.id,
                        # Adding order reference for traceability (assuming origin captures pos reference)
                        'origin': self.origin or line.order_id.name,
                    })
                    
            if move_vals:
                moves = self.env['stock.move'].create(move_vals)
                confirmed_moves = moves._action_confirm()
                
                # Assign quantities to done (equivalent to _add_mls_related_to_order for phantom boms)
                for move in confirmed_moves:
                    move.quantity = move.product_uom_qty
                
                confirmed_moves.picked = True
