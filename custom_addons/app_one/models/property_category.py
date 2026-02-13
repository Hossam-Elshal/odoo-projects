from email.policy import default

from odoo import models, fields

class PropertyCategory(models.Model):
    _name = 'property.category'
    _description = "Property Category"


    # name = fields.Char(required=True, string='Role', default='administrator')


    name = fields.Selection([
        ('administrator', 'مسؤول'),
        ('supervisor', 'Supervisor'),
    ], required=True, string='Role', default='supervisor')

    category_manager_id = fields.Many2one('res.users',string='Category Manager',required=True)

