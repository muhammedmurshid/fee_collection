from odoo import http
from odoo.http import request
import io
import base64
import logging


class QuickPayController(http.Controller):
    # @http.route(['/quick_pay'], type='http', auth="public", website=True, method=['POST'])
    # def quick_pay_form(self):
    #     return request.render("fee_collection.quick_pay_web_form")

    @http.route(['/quick_pay'], type='http', csrf=False, auth='public', website=True, method=['POST'])
    def quick_pay(self, **kw):
        request.env['fee.quick.pay'].sudo().create({
            'admission_no': kw.get('admission_no'),
            'other_client': kw.get('other_client'),
            'other_purpose': kw.get('other_purpose'),
            'other_amount': kw.get('other_amount'),
            'other_phone': kw.get('other_phone'),
            'role': kw.get('role'),
            'purpose': kw.get('purpose'),
            'branch': kw.get('branch'),
            'batch': kw.get('batch'),
            'name': kw.get('name'),
            'phone': kw.get('phone'),
            'amount': kw.get('amount'),
            'refno': kw.get('refno'),

        })
        # print('ok', kw)
        # return request.render("fee_collection.logic_quick_pay_form_success")