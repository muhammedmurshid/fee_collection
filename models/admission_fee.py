from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import ValidationError, UserError


class FeeCollection(models.Model):
    _name = 'admission.fee.collection'
    _description = 'Fee Collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    name = fields.Many2one('logic.students', string='Student Name', required=True)
    batch_id = fields.Many2one('logic.base.batch', string='Batch', required=True, related='name.batch_id', readonly=False)
    mobile_number = fields.Char(string='Mobile Number', related='name.phone_number', readonly=False)
    email = fields.Char(string='Email', related='name.email', readonly=False)
    admission_officer_id = fields.Many2one('res.users', string='Admission Officer',
                                           compute='_compute_get_student_adm_officer', store=True)
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque'), ('online', 'Online')],
                                    string='Payment Mode', )
    admission_id = fields.Char(string='Admission No')
    admission_fee = fields.Float(string='Admission Fee', compute='_onchange_batch_id', store=True, )
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

    def _compute_display_name(self):
        for rec in self:
            if rec.invoice_date:
                rec.display_name = str(rec.invoice_date) + '-' + 'Admission Fee' + '-' + rec.name.name
            else:
                rec.display_name = rec.name.name

    @api.model
    def create(self, vals):
        if vals.get('reference_no', 'New') == 'New':
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'admission.fee.collection') or _('New')

        res = super(FeeCollection, self).create(vals)
        return res

    def action_print_receipt(self):
        return self.env.ref(
            'fee_collection.fee_collection_admission_fee_template_report').report_action(self)

    @api.depends('name')
    def _compute_get_student_adm_officer(self):
        for i in self:
            student = self.env['logic.students'].sudo().search([('id', '=', i.name.id)])
            i.admission_officer_id = student.admission_officer

    @api.depends('paid_amount', 'name', 'batch_id')
    def _compute_pending_amount(self):
        for i in self:
            student = self.env['logic.students'].sudo().search([('id', '=', i.name.id)])
            if student.admission_fee != 0:
                i.pending_amt_student = student.admission_fee - student.paid_amount
            else:
                if i.batch_id:
                    i.pending_amt_student = i.batch_id.admission_fee
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

    @api.depends('batch_id')
    def _onchange_batch_id(self):
        print('nnn')
        if self.batch_id:
            self.admission_fee = self.batch_id.admission_fee

    def action_paid(self):
        if not self.payment_mode:
            raise UserError(_('Please Select Payment Mode'))
        elif self.paid_amount == 0:
            raise UserError(_('Please Enter Paid Amount'))
        else:
            today = datetime.now()
            print('today', today)
            year = today.year
            next_year = year + 1
            next_year_last_two_digits = next_year % 100
            self.admission_id = 'L' + str(year) + '/' + str(self.id)
            fiscal_year = ''
            fiscal = self.env['account.fiscal.year'].search([])
            for i in fiscal:
                for j in self:
                    if i.date_from <= j.invoice_date <= i.date_to:
                        fiscal_year += i.name
            print(fiscal_year, 'fiscal')
            student = self.env['logic.students'].sudo().search([('id', '=', self.name.id)])
            if self.paid_amount:
                if self.paid_amount != 0:
                    if student.paid_amount == 0:
                        student.adm_fee_due_amount = self.admission_fee - self.paid_amount
                        student.pending_amount = ' ' + ':' + ' ' + str(
                            student.adm_fee_due_amount) + ' ' + 'Pending'
                    else:
                        student.adm_fee_due_amount = self.pending_amt_student - self.paid_amount
                        student.pending_amount = ' ' + ':' + ' ' + str(
                            student.adm_fee_due_amount) + ' ' + 'Pending'
            student.admission_no = self.admission_id
            student.admission_fee = self.admission_fee
            student.paid_amount = self.paid_amount + self.name.paid_amount

            receipt_no = self.env['old.fee.receipt.data'].sudo().search([], order='receipt_no desc', limit=1)

            self.payment_reference = 'JK' + '-' + str(fiscal_year) + '/' + str(receipt_no.receipt_no + 1)
            self.state = 'paid'
            receipt = self.env['old.fee.receipt.data'].sudo().create({
                'receipt_no': receipt_no.receipt_no + 1,
                'student_id': self.name.id
            })
