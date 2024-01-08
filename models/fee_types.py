from odoo import models, fields, api, _


class FeeTypesCollections(models.Model):
    _name = 'fee_types.collections'
    _description = 'Fee Types Collections'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Type', required=True)
