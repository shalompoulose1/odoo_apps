from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBarcodeSaleOrder(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'Test Pricelist',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Customer',
            'property_product_pricelist': cls.pricelist.id,
        })
        cls.uom_dozen = cls.env.ref('uom.product_uom_dozen')
        cls.product_a = cls.env['product.product'].create({
            'name': 'Test Product A',
            'barcode': '1111111111111',
            'list_price': 10.0,
            'uom_id': cls.uom_dozen.id,
            'uom_po_id': cls.uom_dozen.id,
        })
        cls.product_b = cls.env['product.product'].create({
            'name': 'Test Product B',
            'barcode': '2222222222222',
            'list_price': 25.0,
        })
        cls.product_no_barcode = cls.env['product.product'].create({
            'name': 'Test Product No Barcode',
            'list_price': 5.0,
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'pricelist_id': cls.pricelist.id,
        })
        cls.salesman = cls.env['res.users'].create({
            'name': 'Test Salesman',
            'login': 'test_salesman',
            'groups_id': [(6, 0, [cls.env.ref('sales_team.group_sale_salesman').id])],
        })
        cls.no_access_user = cls.env['res.users'].create({
            'name': 'Test No Access',
            'login': 'test_no_access',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })

    def test_01_product_found_by_barcode(self):
        product = self.env['product.product'].search([('barcode', '=', self.product_a.barcode)], limit=1)
        self.assertEqual(product, self.product_a)

    def test_02_unknown_barcode_returns_not_found(self):
        result = self.order.action_scan_barcode('0000000000000')
        self.assertEqual(result['status'], 'not_found')
        self.assertFalse(self.order.order_line)

    def test_03_first_scan_creates_line(self):
        result = self.order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(result['status'], 'ok')
        line = self.order.order_line.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_uom_qty, 1)

    def test_04_second_scan_increases_quantity(self):
        self.order.action_scan_barcode(self.product_a.barcode)
        self.order.action_scan_barcode(self.product_a.barcode)
        line = self.order.order_line.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_uom_qty, 2)

    def test_05_multiple_products_create_correct_lines(self):
        self.order.action_scan_barcode(self.product_a.barcode)
        self.order.action_scan_barcode(self.product_b.barcode)
        self.assertEqual(len(self.order.order_line), 2)
        line_a = self.order.order_line.filtered(lambda l: l.product_id == self.product_a)
        line_b = self.order.order_line.filtered(lambda l: l.product_id == self.product_b)
        self.assertEqual(line_a.product_uom_qty, 1)
        self.assertEqual(line_b.product_uom_qty, 1)

    def test_06_existing_manual_quantity_is_incremented(self):
        line = self.env['sale.order.line'].create({
            'order_id': self.order.id,
            'product_id': self.product_a.id,
            'product_uom_qty': 5,
        })
        self.order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(line.product_uom_qty, 6)

    def test_07_pricelist_price_is_respected(self):
        self.env['product.pricelist.item'].create({
            'pricelist_id': self.pricelist.id,
            'applied_on': '0_product_variant',
            'product_id': self.product_a.id,
            'compute_price': 'fixed',
            'fixed_price': 3.33,
        })
        self.order.action_scan_barcode(self.product_a.barcode)
        line = self.order.order_line.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(line.price_unit, 3.33)

    def test_08_product_uom_is_respected(self):
        self.order.action_scan_barcode(self.product_a.barcode)
        line = self.order.order_line.filtered(lambda l: l.product_id == self.product_a)
        self.assertEqual(line.product_uom_id, self.uom_dozen)

    def test_09_customer_is_preserved(self):
        self.order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(self.order.partner_id, self.partner)

    def test_10_confirmed_order_cannot_be_modified(self):
        self.order.action_scan_barcode(self.product_a.barcode)
        self.order.action_confirm()
        self.order.locked = True
        result = self.order.action_scan_barcode(self.product_b.barcode)
        self.assertEqual(result['status'], 'error')
        self.assertFalse(self.order.order_line.filtered(lambda l: l.product_id == self.product_b))

    def test_11_cancelled_order_cannot_be_modified(self):
        self.order.action_confirm()
        self.order.locked = False
        self.order._action_cancel()
        result = self.order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(result['status'], 'error')

    def test_12_access_rights_are_respected(self):
        order = self.order.with_user(self.no_access_user)
        with self.assertRaises(AccessError):
            order.action_scan_barcode(self.product_a.barcode)

    def test_13_empty_barcode_returns_error(self):
        result = self.order.action_scan_barcode('')
        self.assertEqual(result['status'], 'error')

    def test_14_product_without_barcode_not_matched_by_empty_scan(self):
        result = self.order.action_scan_barcode('')
        self.assertNotEqual(result.get('product_name'), self.product_no_barcode.display_name)

    def test_15_archived_product_not_found(self):
        self.product_a.action_archive()
        result = self.order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(result['status'], 'not_found')

    def test_16_salesman_can_scan(self):
        order = self.order.with_user(self.salesman)
        result = order.action_scan_barcode(self.product_a.barcode)
        self.assertEqual(result['status'], 'ok')
