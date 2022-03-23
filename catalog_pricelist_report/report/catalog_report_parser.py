# See LICENSE file for full copyright and licensing details.
from odoo import api, models
from odoo.tools import float_round


class CatalogReport(models.AbstractModel):
    """Catalog report."""

    _name = 'report.catalog_pricelist_report.catalog_report'
    _description = "Catalog report."

    def _get_categorie_data(self, products, product_quantities, pricelist):
        categ_lst = []
        categories_data = self.env['product.category']
        for product in products:
            categories_data |= product.categ_id

        for category in categories_data:
            products_categ = products.filtered(
                lambda product: product.categ_id == category)
            prices = {}
            for categ_product in products_categ:
                prices[categ_product.id] = dict.fromkeys(
                    product_quantities, 0.0)
                for quantity in product_quantities:
                    prices[categ_product.id][quantity] = self._get_price_data(
                        pricelist, categ_product, quantity)
            categ_lst.append({
                'category': category,
                'products': products_categ,
                'prices': prices,
            })
        return categ_lst

    def _quantity(self, data):
        """Get Product Quantity."""
        form = data and data.get('form') or {}
        return sorted([form[key] for key in form if key.startswith('qty') and
                       form[key]])

    @api.model
    def _get_report_values(self, docids, data=None):
        rate = 0.0
        pricelist = False
        symbol = ''
        currency_name = ''
        docs = self.env['product.product'].browse(data.get('ids'))
        product_quantities = self._quantity(data)
        if data['form']['pricelist_id']:
            pricelist = self.env['product.pricelist'].browse(
                data['form']['pricelist_id'][0])
            currency_name = pricelist and \
                pricelist.currency_id.name or False
            symbol = pricelist.currency_id.symbol or False

        return {
            'doc_ids': docs,
            'doc_model': 'product.product',
            'docs': docs,
            'test': data,
            'rate': rate or 00,
            'symbol': symbol or False,
            'currency_name': currency_name or False,
            'data': dict(
                data,
                quantities=product_quantities,
                categories_data=self._get_categorie_data(
                    docs, product_quantities, pricelist)
            ),

        }

    def _get_price_data(self, pricelist, prod, qty):
        sale_price = self.env[
            'decimal.precision'].precision_get('Product Price')
        price = {}
        if pricelist:
            price = pricelist.get_product_price(prod, qty, False)
        if not price:
            price = prod.list_price
        return round(float_round(price, precision_digits=sale_price),2)
