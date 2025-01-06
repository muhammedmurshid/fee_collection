# from odoo import http
# from odoo.http import request
# import io
# import base64
# import logging
# from odoo.http import Response
#
# # class QuickPayController(http.Controller):
# #     @http.route(['/quick_pay'], type='http', auth="public", website=True, method=['POST'])
# #     def quick_pay_form(self):
# #         return request.render("fee_collection.quick_pay_web_form")
#
# #     @http.route(['/quick_pay/submit'], type='http', csrf=False, auth='public', website=True, method=['POST'])
# #     def quick_pay(self, **kwargs):
# #         print(kwargs)
# #         name = kwargs.get('name', '')
# #         purpose = kwargs.get('type', '')
# #         amount = kwargs.get('amount', '')
# #         phone = kwargs.get('phone', '')
# #         refno = kwargs.get('refno', '')
# #         branch = kwargs.get('branch')
# #         admission_number = kwargs.get('admission_no')
# #         batch = kwargs.get('batch')
# #         email_id = kwargs.get('email_id')
# #
# #         web = request.env['res.company'].sudo().search([('name', '=', 'LOGIC MANAGEMENT TRAINING INSTITUTE PVT LTD')],
# #                                                        limit=1)
# #         website = web.website
# #         print(website, 'website')
# #
# #         records = request.env['fee.quick.pay'].sudo().create({
# #             'admission_no': kwargs.get('admission_no'),
# #             'other_client': kwargs.get('other_client'),
# #             'other_purpose': kwargs.get('other_purpose'),
# #             'other_amount': kwargs.get('other_amount'),
# #             'other_phone': kwargs.get('other_phone'),
# #             'role': kwargs.get('role'),
# #             'purpose': kwargs.get('purpose'),
# #             'branch': kwargs.get('branch'),
# #             'batch': kwargs.get('batch'),
# #             'name': kwargs.get('name'),
# #             'phone': kwargs.get('phone'),
# #             'amount': kwargs.get('amount'),
# #             'refno': kwargs.get('refno'),
# #         })
# #
# #         payment_url = f"{website}/payment_form?Name={name}&Purpose={purpose}&Amount={amount}&Phone={phone}&Refno={refno}&branch={branch}&email_id={email_id}&batch={batch}&admission_number={admission_number}"
# #
# #         request.session['payment_url'] = payment_url
# #
# #         # Redirect to the success page
# #         return request.redirect('/quick_pay/success')
#
# class QuickPayController(http.Controller):
#     @http.route(['/quick_pay'], type='http', auth="public", website=True, method=['POST'])
#     def quick_pay_form(self):
#         return request.render("fee_collection.quick_pay_web_form")
#
#     @http.route(['/quick_pay'], type='http', auth="public", methods=['GET'])
#     def quick_pay(self, **kwargs):
#         try:
#             name = kwargs.get('name', '')
#             purpose = kwargs.get('type', '')
#             amount = kwargs.get('amount', '')
#             phone = kwargs.get('phone', '')
#             refno = kwargs.get('refno', '')
#             branch = kwargs.get('branch')
#             admission_number = kwargs.get('admission_no')
#             batch = kwargs.get('batch')
#             email_id = kwargs.get('email_id')
#
#             web = request.env['res.company'].sudo().search(
#                 [('name', '=', 'LOGIC MANAGEMENT TRAINING INSTITUTE PVT LTD')], limit=1)
#             website = web.website
#             if not website:
#                 return Response(
#                     '{"error": "Website not found for the specified company"}',
#                     status=400,
#                     content_type='application/json'
#                 )
#
#             record = request.env['fee.quick.pay'].sudo().create({
#                 'admission_no': admission_number,
#                 'other_client': kwargs.get('other_client'),
#                 'other_purpose': kwargs.get('other_purpose'),
#                 'other_amount': kwargs.get('other_amount'),
#                 'other_phone': kwargs.get('other_phone'),
#                 'role': kwargs.get('role'),
#                 'purpose': purpose,
#                 'branch': branch,
#                 'batch': batch,
#                 'name': name,
#                 'phone': phone,
#                 'amount': amount,
#                 'refno': refno,
#             })
#
#             payment_url = (
#                 f"{website}/payment_form?"
#                 f"Name={name}&Purpose={purpose}&Amount={amount}&Phone={phone}&Refno={refno}&"
#                 f"branch={branch}&email_id={email_id}&batch={batch}&admission_number={admission_number}"
#             )
#
#             response_data = {
#                 'status': 'success',
#                 'message': 'Quick pay record created successfully',
#                 'payment_url': payment_url,
#                 'record_id': record.id
#             }
#
#             return Response(
#                 json.dumps(response_data),
#                 status=200,
#                 content_type='application/json'
#             )
#         except Exception as e:
#             error_response = {'error': f"An error occurred: {str(e)}"}
#             return Response(
#                 json.dumps(error_response),
#                 status=500,
#                 content_type='application/json'
#             )
#
#     @http.route(['/quick_pay/success'], type='http', auth='public', website=True)
#     def quick_pay_success(self):
#         payment_url = request.session.get('payment_url', '')
#         print(payment_url, 'urlll')
#         return request.render('fee_collection.logic_quick_pay_form_success', {'payment_url': payment_url})
#
from odoo import http
from odoo.http import request, Response
import json

class QuickPayController(http.Controller):

    @http.route(['/quick_pay'], type='http', auth="public", methods=['GET'])
    def quick_pay(self, **kwargs):
        try:
            # Validate incoming parameters
            name = kwargs.get('Name')
            purpose = kwargs.get('Purpose')
            amount = kwargs.get('Amount')
            phone = kwargs.get('Phone')
            if not name or not purpose or not amount or not phone:
                return Response(
                    json.dumps({'error': 'Missing required parameters'}),
                    status=400,
                    content_type='application/json'
                )

            # Create record in 'fee.quick.pay'
            print('kwrag', kwargs)
            record = request.env['fee.quick.pay'].sudo().create({
                'name': name,
                'purpose': purpose,
                'amount': float(amount),
                'phone': phone,
                'refno': kwargs.get('Refno'),
                'branch': kwargs.get('branch'),
                # 'email_id': kwargs.get('email_id'),
                'batch': kwargs.get('batch'),
                'admission_no': kwargs.get('admission_number'),
            })

            # Return success response
            response_data = {
                'status': 'success',
                'message': 'Quick pay record created successfully',
                'record_id': record.id
            }
            return Response(
                json.dumps(response_data),
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            # Return error response
            error_response = {
                'status': 'error',
                'message': f"An error occurred: {str(e)}"
            }
            return Response(
                json.dumps(error_response),
                status=500,
                content_type='application/json'
            )
