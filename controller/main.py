from odoo import http
from odoo.http import request
import io
import base64
import logging


class QuickPayController(http.Controller):
    @http.route(['/quick_pay'], type='http', auth="public", website=True, method=['POST'])
    def quick_pay_form(self):
        return request.render("fee_collection.quick_pay_web_form")

    @http.route(['/quick_pay/submit'], type='http', csrf=False, auth='public', website=True, method=['POST'])
    def quick_pay(self, **kwargs):
        print(kwargs)
        name = kwargs.get('name', '')
        purpose = kwargs.get('type', '')
        amount = kwargs.get('amount', '')
        phone = kwargs.get('phone', '')
        refno = kwargs.get('refno', '')
        branch = kwargs.get('branch')
        admission_number = kwargs.get('admission_no')
        batch = kwargs.get('batch')
        email_id = kwargs.get('email_id')

        web = request.env['res.company'].sudo().search([('name', '=', 'LOGIC MANAGEMENT TRAINING INSTITUTE PVT LTD')], limit=1)
        website = web.website
        print(website, 'website')

        payment_url = f"{website}/payment_form?Name={name}&Purpose={purpose}&Amount={amount}&Phone={phone}&Refno={refno}&branch={branch}&email_id={email_id}&batch={batch}&admission_number={admission_number}"

        return request.redirect(payment_url)
        # request.env['fee.quick.pay'].sudo().create({
        #     'admission_no': kw.get('admission_no'),
        #     'other_client': kw.get('other_client'),
        #     'other_purpose': kw.get('other_purpose'),
        #     'other_amount': kw.get('other_amount'),
        #     'other_phone': kw.get('other_phone'),
        #     'role': kw.get('role'),
        #     'purpose': kw.get('purpose'),
        #     'branch': kw.get('branch'),
        #     'batch': kw.get('batch'),
        #     'name': kw.get('name'),
        #     'phone': kw.get('phone'),
        #     'amount': kw.get('amount'),
        #     'refno': kw.get('refno'),
        #
        # })
        # print('ok', kw)
        # return request.render("fee_collection.logic_quick_pay_form_success")

    @http.route('/payment_form/submit', type='http', auth='public', website=True, methods=['POST'], csrf=False)
    def payment_form_submit(self, **kwargs):
        # Extract form values
        print(kwargs)
        name = kwargs.get('name_of_student', '')
        purpose = kwargs.get('Purpose', '')
        amount = kwargs.get('amount', '')
        phone = kwargs.get('phone_number', '')
        refno = kwargs.get('Refno', '')
        branch = kwargs.get('branch')
        admission_number = kwargs.get('admission_number')
        batch = kwargs.get('batch')
        email_id = kwargs.get('email_id')

        payment_url = f"http://localhost:8069/payment_form?Name={name}&Purpose={purpose}&Amount={amount}&Phone={phone}&Refno={refno}&branch={branch}&email_id={email_id}&batch={batch}&admission_number={admission_number}"

        return request.redirect(payment_url)