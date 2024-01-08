from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError, UserError


class CourseFeeCollection(models.Model):
    _name = "course.fee.collection"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Course Fee Collection'
    _rec_name = 'display_name'

    student_id = fields.Many2one('logic.students', string='Student Name', required=True)
    batch_id = fields.Many2one('logic.base.batch', string='Batch', required=True, related='student_id.batch_id',
                               readonly=False)
    mobile_number = fields.Char(string='Mobile Number', related='student_id.phone_number', readonly=False)
    email = fields.Char(string='Email', related='student_id.email', readonly=False)
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque'), ('online', 'Online')],
                                    string='Payment Mode', default='online')
    admission_id = fields.Char(string='Admission No', related='student_id.admission_no')
    paid_amount = fields.Float(string='Paid Amount')
    invoice_date = fields.Date(string='Invoice Date', required=True, default=fields.Date.today())
    payment_reference = fields.Char(string='Payment Reference')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    amount_cgst = fields.Float(string='CGST', compute='_compute_amount_cgst', store=True)
    amount_sgst = fields.Float(string='SGST', compute='_compute_amount_sgst', store=True)
    amount_gst = fields.Float(string='GST', compute='_compute_amount_gst', store=True)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default='draft', string='Status')
    pending_amt_student = fields.Float(string='Pending Amount', compute='_compute_pending_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    reference_no = fields.Char(string='Payment SI Number', required=True,
                               readonly=False, default=lambda self: _('New'))
    cheque_number = fields.Char(string='Cheque No / Reference No')
    course_id = fields.Many2one('logic.base.courses', string='Course', related='batch_id.course_id')
    course_fee = fields.Float(string='Course Fee', compute='_compute_course_fee', store=True)

    @api.model
    def create(self, vals):
        if vals.get('reference_no', 'New') == 'New':
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'course.fee.collection') or _('New')
        res = super(CourseFeeCollection, self).create(vals)
        return res

    def _compute_display_name(self):
        for rec in self:
            if rec.invoice_date:
                rec.display_name = str(rec.invoice_date) + '-' + rec.student_id.name
            else:
                rec.display_name = rec.student_id.name

    @api.depends('batch_id')
    def _compute_course_fee(self):
        for i in self:
            course_fee = self.env['logic.base.batch'].sudo().search([('id', '=', i.batch_id.id)])
            print(course_fee, 'course_fee')
            i.course_fee = course_fee.course_fee

    @api.depends('paid_amount', 'student_id', 'batch_id')
    def _compute_pending_amount(self):
        for i in self:
            student = self.env['logic.students'].sudo().search([('id', '=', i.student_id.id)])
            if student.course_fee != 0:
                i.pending_amt_student = student.course_fee - student.paid_course_fee
            else:
                if i.batch_id:
                    i.pending_amt_student = i.batch_id.course_fee
                else:
                    i.pending_amt_student = 0

    @api.depends('amount_cgst', 'paid_amount')
    def _compute_amount_cgst(self):
        for i in self:
            i.amount_cgst = (9 / 100) * i.paid_amount

    taxable_amount = fields.Float(string='taxable Amount', compute='_compute_taxable_amount', store=True)

    @api.depends('amount_sgst', 'paid_amount')
    def _compute_amount_sgst(self):
        for i in self:
            i.amount_sgst = (9 / 100) * i.paid_amount

    @api.depends('amount_sgst', 'amount_sgst', 'paid_amount')
    def _compute_amount_gst(self):
        for i in self:
            i.amount_gst = i.amount_sgst + i.amount_cgst

    @api.depends('paid_amount', 'amount_gst')
    def _compute_taxable_amount(self):
        for i in self:
            i.taxable_amount = i.paid_amount - i.amount_gst

    def _compute_total_amount_in_words(self, doc):
        # INR = self.env['res.currency'].search([('name', '=', 'INR')])
        for move in doc:
            if move.paid_amount:
                total = move.paid_amount
                y = move.currency_id.amount_to_text(total)
                return str(y)

    def action_paid(self):
        if self.paid_amount == 0:
            raise UserError(_('Please Enter Paid Amount'))
        else:
            fiscal_year = ''
            fiscal = self.env['account.fiscal.year'].search([])
            for i in fiscal:
                for j in self:
                    if i.date_from <= j.invoice_date <= i.date_to:
                        fiscal_year += i.name
            print(fiscal_year, 'fiscal')
            student = self.env['logic.students'].sudo().search([('id', '=', self.student_id.id)])
            if self.paid_amount:
                if self.paid_amount != 0:
                    if student.paid_course_fee == 0:
                        student.course_due_amount = self.course_fee - self.paid_amount
                        student.course_pending_amount = ' ' + ':' + ' ' + str(
                            student.course_due_amount) + ' ' + 'Pending'
                    else:
                        student.course_due_amount = self.pending_amt_student - self.paid_amount
                        student.course_pending_amount = ' ' + ':' + ' ' + str(
                            student.course_due_amount) + ' ' + 'Pending'

            student.course_fee = self.course_fee
            student.paid_course_fee = self.paid_amount + self.student_id.paid_course_fee
            receipt_no = self.env['old.fee.receipt.data'].sudo().search([], order='receipt_no desc', limit=1)

            today = datetime.now()
            print('today', today)
            year = today.year
            next_year = year + 1
            next_year_last_two_digits = next_year % 100

            self.payment_reference = 'JK' + '-' + str(fiscal_year) + '/' + str(receipt_no.receipt_no + 1)
            self.state = 'paid'

            receipt = self.env['old.fee.receipt.data'].sudo().create({
                'receipt_no': receipt_no.receipt_no + 1,
                'student_id': self.student_id.id
            })

    def action_course_fee_print_receipt(self):
        return self.env.ref(
            'fee_collection.fee_collection_course_fee_template_report').report_action(self)
