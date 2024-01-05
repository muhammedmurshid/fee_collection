from odoo import models, fields, api, _


class FeeQuickPayLogic(models.Model):
    _name = 'fee.quick.pay'
    _description = 'Fee Quick Pay'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    admission_no = fields.Char(string='Name')
    other_client = fields.Char(string='Other Client')
    other_purpose = fields.Char(string='Other Purpose')
    other_amount = fields.Char(string='Other Amount')
    other_phone = fields.Char(string='Other Phone')
    role = fields.Char(string='Role')
    purpose = fields.Char(string='Purpose')
    branch = fields.Char(string='Branch')
    batch = fields.Char(string='Batch')
    name = fields.Char(string='Name')
    phone = fields.Char(string='Phone')
    amount = fields.Char(string='Amount')
    refno = fields.Char(string='Ref No')
