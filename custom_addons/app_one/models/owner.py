from odoo import models, fields

class Owner(models.Model):
    _name = 'owner'

    name = fields.Char(required=1)
    phone = fields.Char()
    address = fields.Char(translate=True)

    #one2many => computed relation
    property_ids = fields.One2many('property', 'owner_id')


    #Field in property Model=> owner_id = fields.Many2one('owner')