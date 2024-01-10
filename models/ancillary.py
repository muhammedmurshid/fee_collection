from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class AncillaryFeeCollection(models.Model):
    _name = 'ancillary.fee.collection'
    _description = 'Ancillary Fee Collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('logic.students', required=True)
    fee_type = fields.Many2one('fee_types.collections', 'Fee Type', required=True)
    batch_id = fields.Many2one('logic.base.batch', string='Batch', required=True, related='name.batch_id', readonly=False)
    mobile_number = fields.Char(string='Mobile Number', related='name.phone_number', readonly=False)
    email = fields.Char(string='Email', related='name.email', readonly=False)
    payment_mode = fields.Selection([('cash', 'Cash'), ('cheque', 'Cheque'), ('online', 'Online')], string='Payment Mode', required=1)
    paid_amount = fields.Float(string='Paid Amount')
    invoice_date = fields.Date(string='Invoice Date', required=True, default=fields.Date.today())
    payment_reference = fields.Char(string='Payment Reference')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid'), ('credit_note', 'Credit Note')], default='draft', string='Status')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    reference_no = fields.Char(string='Payment SI Number', required=True, readonly=False, default=lambda self: _('New'))
    cheque_number = fields.Char(string='Cheque No / Reference No')

    def action_paid(self):
        today = datetime.now()
        print('today', today)
        year = today.year
        next_year = year + 1
        next_year_last_two_digits = next_year % 100
        fiscal_year = ''
        fiscal = self.env['account.fiscal.year'].search([])
        for i in fiscal:
            for j in self:
                if i.date_from <= j.invoice_date <= i.date_to:
                    fiscal_year += i.name
        print(fiscal_year, 'fiscal')

        receipt_no = self.env['ancillary.receipt.data'].sudo().search([], order='receipt_no desc', limit=1)

        self.payment_reference = 'JK' + '-' + str(fiscal_year) + '/' + str(receipt_no.receipt_no + 1)
        self.state = 'paid'
        receipt = self.env['ancillary.receipt.data'].sudo().create({
            'receipt_no': receipt_no.receipt_no + 1,
            'student_id': self.name.id
        })
        student = self.env['logic.students'].sudo().search([('id', '=', self.name.id)])
        print(student.name, 'students')
        student.write({
            'ancillary_fee_ids': [(0, 0, {'fee_type': self.fee_type.name, 'amount': self.paid_amount})]
        })
        # if self.fee_ref_no == 0:
        #     self.fee_ref_no = ref_no.fee_ref_no + 1
        # if self.paid_amount == 0:
        #     raise ValidationError(_('Please enter paid amount'))
        # else:
        #     self.state = 'paid'

    def _compute_total_amount_in_words(self, doc):
        # INR = self.env['res.currency'].search([('name', '=', 'INR')])
        for move in doc:
            if move.paid_amount:
                total = move.paid_amount
                y = move.currency_id.amount_to_text(total)
                return str(y)

    def action_ancillary_fee_print_receipt(self):
        return self.env.ref(
            'fee_collection.ancillary_fee_template_report').report_action(self)

    # def action_sample_add_students_fee(self):
    #     student = self.env['logic.students'].sudo().search([('id', '=', self.name.id)])
    #     print(student.name, 'students')
    #     student.write({
    #         'ancillary_fee_ids': [(0, 0, {'fee_type': self.fee_type.name, 'amount': self.paid_amount})]
    #     })

    credit_no = fields.Char(string='Credit No')

    def action_credit_note(self):
        fiscal_year = ''
        fiscal = self.env['account.fiscal.year'].search([])
        for i in fiscal:
            if i.date_from <= self.invoice_date <= i.date_to:
                fiscal_year += i.name
        print(fiscal_year, 'fiscal')
        print('credit note')
        receipt_no = self.env['credit.note.fee.collection'].sudo().search([], order='receipt_no desc', limit=1)

        self.credit_no = 'JK' + '-' + str(fiscal_year) + '/' + str(receipt_no.receipt_no + 1)
        receipt = self.env['credit.note.fee.collection'].sudo().create({
            'receipt_no': receipt_no.receipt_no + 1,
            'student_id': self.name.id
        })
        self.write({
            'state': 'credit_note'
        })

    def action_print_credit_note(self):
        return self.env.ref(
            'fee_collection.ancillary_credit_note_report').report_action(self)
