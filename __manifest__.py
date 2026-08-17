{
    'name': 'SLV POS Product BoM',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Custom Bill of Materials (BoM) system for POS products.',
    'description': """
        Develop a modular Odoo 18.0 addon named pos_product_bom that introduces a custom Bill of Materials (BoM) system for POS restaurant products. 
        When a finished food item is sold in POS, the system must explode its BoM and deduct raw ingredients from stock instead of the finished product.
    """,
    'author': 'Antigravity',
    'depends': ['point_of_sale', 'stock'],
    'data': [
        'security/pos_bom_security.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/pos_product_bom_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
