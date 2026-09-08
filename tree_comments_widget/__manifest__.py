{
    'name': 'Tree Comments Widget',
    'summary': 'Generic floating comments popup widget for any list view.',
    'description': """
Tree Comments Widget
=====================

A generic floating comments popup you can drop into any list view column.
Adds an inline "Comments" button with an unread-style count badge; clicking
it opens a small popup showing that record's chatter comments, with
@mention autocomplete and Ctrl+Enter to post.

Key Features
-------------
* Reusable comments button field widget for any list view
* Floating popup positioned next to the clicked row, no page navigation
* @mention autocomplete against res.partner users
* Posts through the standard mail.thread message_post flow
* Comment count badge kept up to date after posting
* Drop-in mixin (`tree.comments.mixin`) to add the count field to any model

Designed for Odoo 19.0.

See README.md for detailed configuration and usage instructions.
""",
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'author': 'MD ERP Solutions',
    'support': 'mrdudedeg@gmail.com',
    'license': 'OPL-1',
    'price': 29.00,
    'currency': 'USD',

    'depends': [
        'mail',
    ],

    'data': [],

    'demo': [],

    'assets': {
        'web.assets_backend': [
            'tree_comments_widget/static/src/css/tree_comments.css',
            'tree_comments_widget/static/src/js/tree_comments.js',
            'tree_comments_widget/static/src/xml/tree_comments.xml',
        ],
    },

    'images': [
        'static/description/banner.png',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
