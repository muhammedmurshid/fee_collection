from odoo import models, fields, api, _


class OldFeeData(models.Model):
    _name = 'old.fee.receipt.data'

    receipt_no = fields.Integer(string='Receipt No')
    student_id = fields.Many2one('logic.students', string='Student')


class OldCourseFeeData(models.Model):
    _name = 'old.course.fee.data'

    receipt_no = fields.Integer('Receipt No')
    student_id = fields.Many2one('logic.students', string='Student')


class OldTotalFeeCollection(models.Model):
    _name = 'old.total.fee.collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    erp_admission_id = fields.Integer('Erp Id')
    fee_type = fields.Char('Type')
    date = fields.Date('Date')
    amount = fields.Float('Amount')
    receipt_no = fields.Char('Receipt No')

