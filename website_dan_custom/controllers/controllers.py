# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.fields import Command
from odoo.http import request
from odoo.addons.base.models.ir_qweb_fields import nl2br
# omar
# from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment.controllers.post_processing import PaymentPostProcessing
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website.controllers import main
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.osv import expression
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.http import content_disposition, Controller, request, route
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
# omar
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from odoo.tools import lazy
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.addons.website_sale.controllers.main import WebsiteSale

from datetime import datetime
_logger = logging.getLogger(__name__)
class TableCompute(object):

    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey, ppr):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= ppr:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(ppr):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products, ppg=20, ppr=4):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        x = 0
        for p in products:
            x = min(max(p.website_size_x, 1), ppr)
            y = min(max(p.website_size_y, 1), ppr)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % ppr, pos // ppr, x, y, ppr):
                pos += 1
            # if 21st products (index 20) and the last line is full (ppr products in it), break
            # (pos + 1.0) / ppr is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) // ppr) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos // ppr

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos // ppr) + y2][(pos % ppr) + x2] = False
            self.table[pos // ppr][pos % ppr] = {
                'product': p, 'x': x, 'y': y,
                'ribbon': p._get_website_ribbon(),
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos // ppr))
            index += 1

        # Format table according to HTML needs
        rows = sorted(self.table.items())
        rows = [r[1] for r in rows]
        for col in range(len(rows)):
            cols = sorted(rows[col].items())
            x += len(cols)
            rows[col] = [r[1] for r in cols if r[1]]

        return rows

class WebsiteSale(WebsiteSale):

    def _get_pricelist_context(self):
        pricelist_context = dict(request.env.context)
        pricelist = False
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        return pricelist_context, pricelist

    def _get_search_order(self, post):
        # OrderBy will be parsed in orm and so no direct sql injection
        # id is added to be sure that order is a unique sort key
        order = post.get('order') or 'website_sequence ASC'
        return 'is_published desc, %s, id desc' % order

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domains = [request.website.sale_product_domain()]
        if search:
            for srch in search.split(" "):
                subdomains = [
                    [('name', 'ilike', srch)],
                    [('product_variant_ids.default_code', 'ilike', srch)]
                ]
                if search_in_description:
                    subdomains.append([('description', 'ilike', srch)])
                    subdomains.append([('description_sale', 'ilike', srch)])
                domains.append(expression.OR(subdomains))

        if category:
            domains.append([('public_categ_ids', 'child_of', int(category))])

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domains.append([('attribute_line_ids.value_ids', 'in', ids)])
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domains.append([('attribute_line_ids.value_ids', 'in', ids)])

        return expression.AND(domains)

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}

        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    # @http.route([
    #     '''/shop''',
    #     '''/shop/page/<int:page>''',
    #     '''/shop/category/<model("product.public.category"):category>''',
    #     '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    # ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    # def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
    #     add_qty = int(post.get('add_qty', 1))
    #     try:
    #         min_price = float(min_price)
    #     except ValueError:
    #         min_price = 0
    #     try:
    #         max_price = float(max_price)
    #     except ValueError:
    #         max_price = 0
    #
    #     Category = request.env['product.public.category']
    #     if category:
    #         category = Category.search([('id', '=', int(category))], limit=1)
    #         if not category or not category.can_access_from_current_website():
    #             raise NotFound()
    #     else:
    #         category = Category
    #
    #     if ppg:
    #         try:
    #             ppg = int(ppg)
    #             post['ppg'] = ppg
    #         except ValueError:
    #             ppg = False
    #     if not ppg:
    #         ppg = request.env['website'].get_current_website().shop_ppg or 20
    #
    #     ppr = request.env['website'].get_current_website().shop_ppr or 4
    #
    #     attrib_list = request.httprequest.args.getlist('attrib')
    #     attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
    #     attributes_ids = {v[0] for v in attrib_values}
    #     attrib_set = {v[1] for v in attrib_values}
    #
    #     keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, min_price=min_price, max_price=max_price, order=post.get('order'))
    #
    #     pricelist_context, pricelist = self._get_pricelist_context()
    #
    #     request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)
    #
    #     filter_by_price_enabled = request.website.is_view_active('website_sale.filter_products_price')
    #     if filter_by_price_enabled:
    #         company_currency = request.website.company_id.currency_id
    #         conversion_rate = request.env['res.currency']._get_conversion_rate(company_currency, pricelist.currency_id, request.website.company_id, fields.Date.today())
    #     else:
    #         conversion_rate = 1
    #
    #     url = "/shop"
    #     if search:
    #         post["search"] = search
    #     if attrib_list:
    #         post['attrib'] = attrib_list
    #
    #     options = {
    #         'displayDescription': True,
    #         'displayDetail': True,
    #         'displayExtraDetail': True,
    #         'displayExtraLink': True,
    #         'displayImage': True,
    #         'allowFuzzy': not post.get('noFuzzy'),
    #         'category': str(category.id) if category else None,
    #         'min_price': min_price / conversion_rate,
    #         'max_price': max_price / conversion_rate,
    #         'attrib_values': attrib_values,
    #         'display_currency': pricelist.currency_id,
    #     }
    #     # No limit because attributes are obtained from complete product list
    #     product_count, details, fuzzy_search_term = request.website._search_with_fuzzy("products_only", search,
    #         limit=None, order=self._get_search_order(post), options=options)
    #     search_product = details[0].get('results', request.env['product.template']).with_context(bin_size=True)
    #
    #     filter_by_price_enabled = request.website.is_view_active('website_sale.filter_products_price')
    #     if filter_by_price_enabled:
    #         # TODO Find an alternative way to obtain the domain through the search metadata.
    #         Product = request.env['product.template'].with_context(bin_size=True)
    #         domain = self._get_search_domain(search, category, attrib_values)
    #
    #         # This is ~4 times more efficient than a search for the cheapest and most expensive products
    #         from_clause, where_clause, where_params = Product._where_calc(domain).get_sql()
    #         query = f"""
    #             SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
    #               FROM {from_clause}
    #              WHERE {where_clause}
    #         """
    #         request.env.cr.execute(query, where_params)
    #         available_min_price, available_max_price = request.env.cr.fetchone()
    #
    #         if min_price or max_price:
    #             # The if/else condition in the min_price / max_price value assignment
    #             # tackles the case where we switch to a list of products with different
    #             # available min / max prices than the ones set in the previous page.
    #             # In order to have logical results and not yield empty product lists, the
    #             # price filter is set to their respective available prices when the specified
    #             # min exceeds the max, and / or the specified max is lower than the available min.
    #             if min_price:
    #                 min_price = min_price if min_price <= available_max_price else available_min_price
    #                 post['min_price'] = min_price
    #             if max_price:
    #                 max_price = max_price if max_price >= available_min_price else available_max_price
    #                 post['max_price'] = max_price
    #
    #     website_domain = request.website.website_domain()
    #     categs_domain = [('parent_id', '=', False)] + website_domain
    #     if search:
    #         search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
    #         categs_domain.append(('id', 'in', search_categories.ids))
    #     else:
    #         search_categories = Category
    #     categs = Category.search(categs_domain)
    #
    #     if category:
    #         url = "/shop/category/%s" % slug(category)
    #
    #     pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
    #     offset = pager['offset']
    #     products = search_product[offset:offset + ppg]
    #
    #     ProductAttribute = request.env['product.attribute']
    #     if products:
    #         # get all products without limit
    #         attributes = ProductAttribute.search([
    #             ('product_tmpl_ids', 'in', search_product.ids),
    #             ('visibility', '=', 'visible'),
    #         ])
    #     else:
    #         attributes = ProductAttribute.browse(attributes_ids)
    #
    #     layout_mode = request.session.get('website_sale_shop_layout_mode')
    #     if not layout_mode:
    #         if request.website.viewref('website_sale.products_list_view').active:
    #             layout_mode = 'list'
    #         else:
    #             layout_mode = 'grid'
    #     # if
    #     users_id_urrent = request.env['res.users'].sudo().search([('id','=',request.uid)])
    #     if users_id_urrent.x_product_ids:
    #         products = products.search([('id','in', users_id_urrent.x_product_ids.ids)])
    #
    #
    #     values = {
    #         'search': fuzzy_search_term or search,
    #         'original_search': fuzzy_search_term and search,
    #         'category': category,
    #         'attrib_values': attrib_values,
    #         'attrib_set': attrib_set,
    #         'pager': pager,
    #         'pricelist': pricelist,
    #         'add_qty': add_qty,
    #         'products': products,
    #         'search_count': product_count,  # common for all searchbox
    #         'bins': TableCompute().process(products, ppg, ppr),
    #         'ppg': ppg,
    #         'ppr': ppr,
    #         'categories': categs,
    #         'attributes': attributes,
    #         'keep': keep,
    #         'search_categories_ids': search_categories.ids,
    #         'layout_mode': layout_mode,
    #     }
    #     if filter_by_price_enabled:
    #         values['min_price'] = min_price or available_min_price
    #         values['max_price'] = max_price or available_max_price
    #         values['available_min_price'] = tools.float_round(available_min_price, 2)
    #         values['available_max_price'] = tools.float_round(available_max_price, 2)
    #     if category:
    #         values['main_object'] = category
    #     return request.render("website_sale.products", values)
    def _shop_get_query_url_kwargs(self, category, search, min_price, max_price, attrib=None, order=None, **post):
        return {
            'category': category,
            'search': search,
            'attrib': attrib,
            'min_price': min_price,
            'max_price': max_price,
            'order': order,
        }
    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        try:
            min_price = float(min_price)
        except ValueError:
            min_price = 0
        try:
            max_price = float(max_price)
        except ValueError:
            max_price = 0

        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        website = request.env['website'].get_current_website()
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = website.shop_ppg or 20

        ppr = website.shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop',
                        **self._shop_get_query_url_kwargs(category and int(category), search, min_price, max_price,
                                                          **post))

        now = datetime.timestamp(datetime.now())
        pricelist = request.env['product.pricelist'].browse(request.session.get('website_sale_current_pl'))
        if not pricelist or request.session.get('website_sale_pricelist_time',
                                                0) < now - 60 * 60:  # test: 1 hour in session
            pricelist = website.get_current_pricelist()
            request.session['website_sale_pricelist_time'] = now
            request.session['website_sale_current_pl'] = pricelist.id

        request.update_context(pricelist=pricelist.id, partner=request.env.user.partner_id)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            company_currency = website.company_id.currency_id
            conversion_rate = request.env['res.currency']._get_conversion_rate(
                company_currency, pricelist.currency_id, request.website.company_id, fields.Date.today())
        else:
            conversion_rate = 1

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        options = self._get_search_options(
            category=category,
            attrib_values=attrib_values,
            pricelist=pricelist,
            min_price=min_price,
            max_price=max_price,
            conversion_rate=conversion_rate,
            **post
        )
        fuzzy_search_term, product_count, search_product = self._shop_lookup_products(attrib_set, options, post, search,
                                                                                      website)

        filter_by_price_enabled = website.is_view_active('website_sale.filter_products_price')
        if filter_by_price_enabled:
            # TODO Find an alternative way to obtain the domain through the search metadata.
            Product = request.env['product.template'].with_context(bin_size=True)
            domain = self._get_search_domain(search, category, attrib_values)

            # This is ~4 times more efficient than a search for the cheapest and most expensive products
            from_clause, where_clause, where_params = Product._where_calc(domain).get_sql()
            query = f"""
                    SELECT COALESCE(MIN(list_price), 0) * {conversion_rate}, COALESCE(MAX(list_price), 0) * {conversion_rate}
                      FROM {from_clause}
                     WHERE {where_clause}
                """
            request.env.cr.execute(query, where_params)
            available_min_price, available_max_price = request.env.cr.fetchone()

            if min_price or max_price:
                # The if/else condition in the min_price / max_price value assignment
                # tackles the case where we switch to a list of products with different
                # available min / max prices than the ones set in the previous page.
                # In order to have logical results and not yield empty product lists, the
                # price filter is set to their respective available prices when the specified
                # min exceeds the max, and / or the specified max is lower than the available min.
                if min_price:
                    min_price = min_price if min_price <= available_max_price else available_min_price
                    post['min_price'] = min_price
                if max_price:
                    max_price = max_price if max_price >= available_min_price else available_max_price
                    post['max_price'] = max_price

        website_domain = website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search(
                [('product_tmpl_ids', 'in', search_product.ids)] + website_domain
            ).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = lazy(lambda: Category.search(categs_domain))

        if category:
            url = "/shop/category/%s" % slug(category)

        pager = website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        offset = pager['offset']
        products = search_product[offset:offset + ppg]

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = lazy(lambda: ProductAttribute.search([
                ('product_tmpl_ids', 'in', search_product.ids),
                ('visibility', '=', 'visible'),
            ]))
        else:
            attributes = lazy(lambda: ProductAttribute.browse(attributes_ids))

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'
            request.session['website_sale_shop_layout_mode'] = layout_mode

        products_prices = lazy(lambda: products._get_sales_prices(pricelist))
        users_id_urrent = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        if users_id_urrent.x_product_ids:
            products = products.search([('id', 'in', users_id_urrent.x_product_ids.ids)])

        values = {
            'search': fuzzy_search_term or search,
            'original_search': fuzzy_search_term and search,
            'order': post.get('order', ''),
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_product': search_product,
            'search_count': product_count,  # common for all searchbox
            'bins': lazy(lambda: TableCompute().process(products, ppg, ppr)),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
            'products_prices': products_prices,
            'get_product_prices': lambda product: lazy(lambda: products_prices[product.id]),
            'float_round': tools.float_round,
        }
        if filter_by_price_enabled:
            values['min_price'] = min_price or available_min_price
            values['max_price'] = max_price or available_max_price
            values['available_min_price'] = tools.float_round(available_min_price, 2)
            values['available_max_price'] = tools.float_round(available_max_price, 2)
        if category:
            values['main_object'] = category
        values.update(self._get_additional_shop_values(values))
        return request.render("website_sale.products", values)

    def _prepare_product_values(self, product, category, search, **kwargs):
        add_qty = int(kwargs.get('add_qty', 1))

        product_context = dict(request.env.context, quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        min_price = request.params.get('min_price')
        max_price = request.params.get('max_price')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list, min_price=min_price, max_price=max_price)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()

        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        # Needed to trigger the recently viewed product rpc
        view_track = request.website.viewref("website_sale.product").track

        return {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'add_qty': add_qty,
            'view_track': view_track,
        }



class  CustomerPortal(portal.CustomerPortal):
    def _prepare_quotations_domain(self, partner):
        return [
            ('partner_id', '=', partner.id),
            ('state', '=', 'sent')
        ]

    def _prepare_orders_domain(self, partner):
        return [
            ('partner_id', '=', partner.id),
            ('state', 'in', ['sale', 'done'])
        ]

