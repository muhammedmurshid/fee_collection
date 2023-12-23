from odoo import models, fields, api, _


class OldFeeData(models.Model):
    _name = 'old.fee.receipt.data'

    receipt_no = fields.Integer(string='Receipt No')
    student_id = fields.Many2one('logic.students', string='Student')


class OldCourseFeeData(models.Model):
    _name = 'old.course.fee.data'

    receipt_no = fields.Integer('Receipt No')
    student_id = fields.Many2one('logic.students', string='Student')

