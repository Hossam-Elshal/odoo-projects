from odoo import models, fields


class Building(models.Model):
    _name = 'building'
    _description = 'Building Record'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    no = fields.Integer()
    code = fields.Char()
    description = fields.Text()

    # reserved field
    name = fields.Char()
    active = fields.Boolean(default=True) #Archive / Un archive
