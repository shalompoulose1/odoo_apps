{
    'name': 'Barcode Scanning for Sale Orders',
    'summary': 'Scan product barcodes to add or update Sale Order lines.',
    'description': """
Barcode Scanning for Sale Orders
=================================

Quickly add products to Sale Orders by scanning their barcodes directly
from the Sale Order form.

Key Features
-------------
* Scan product barcodes directly from Sale Orders
* Automatically add the matching product
* Increase quantity when the same product is scanned again
* Supports USB keyboard-wedge barcode scanners
* Camera-based barcode scanning where supported
* Product variant barcode support
* Works with existing pricelists, taxes and fiscal positions
* Handles unknown or invalid barcodes
* Fast workflow without manually searching for products

Designed for Odoo 19.0.

See README.md for detailed configuration and usage instructions.
""",
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'author': 'MD ERP Solutions',
    'support': 'mrdudedeg@gmail.com',
    'license': 'OPL-1',

    'depends': [
        'sale',
        'barcodes',
    ],

    'data': [
        'views/sale_order_views.xml',
    ],

    'demo': [],

    'assets': {
        'web.assets_backend': [
            'barcode_sale_order/static/src/js/**/*',
            'barcode_sale_order/static/src/xml/**/*',
            'barcode_sale_order/static/src/scss/**/*',
        ],
    },

    'images': [
        'static/description/banner.png',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
