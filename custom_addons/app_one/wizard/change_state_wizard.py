from odoo import models, fields


class ChangeStateWizard(models.TransientModel):
    _name = 'change_state_wizard'

    property_id = fields.Many2one('property')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
    ])
    reason = fields.Char()

    def action_confirm(self):
        if self.property_id.state == 'closed':
            self.property_id.state = self.state
            self.property_id.create_history_record('closed',self.state, self.reason)


