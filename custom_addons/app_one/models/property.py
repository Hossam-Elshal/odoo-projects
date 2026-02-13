from odoo import models, fields, api  # import api
from odoo.exceptions import ValidationError


class Property(models.Model):
    _name = 'property'
    _description = 'Property'

    _inherit = ['mail.thread', 'mail.activity.mixin']

    ref = fields.Char(default='New', readonly=True)
    name = fields.Char(required=1, default='New', translate=True)
    description = fields.Text()
    postcode = fields.Char(required=1)
    date_availability = fields.Date(tracking=True)

    # Automated Actions Task:
    expected_selling_date = fields.Date(tracking=True)
    is_late = fields.Boolean()

    expected_price = fields.Float()
    selling_price = fields.Float()
    diff = fields.Float(compute='_compute_diff', store=1, readonly=1)

    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garden = fields.Boolean()
    garage = fields.Boolean()

    # Additional Info. #######################
    owner_id = fields.Many2one('owner')  # Relational Field =>  new column (fKey)
    owner_address = fields.Char(related='owner_id.address', translate=True)
    owner_phone = fields.Char(related='owner_id.phone', readonly=0)
    tag_ids = fields.Many2many('tag')  # Relational Field =>  new table => property_tag_rel
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ], default='north')
    category_id = fields.Many2one('property.category', string='Category')
    #########################################################################################
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed', 'Closed'),
    ], default='draft')

    # Data Tier constrain
    _sql_constraints = [
        ('unique_name', 'unique("name")', 'This name is already exist')
    ]
    ############################ Methods #################################################
    # once fields has been changed => call method
    @api.depends('expected_price', 'selling_price')  # simple fields (views or model) or relational fields
    def _compute_diff(self):
        for record in self:
            record.diff = record.expected_price - record.selling_price
            # note: return record

    ##################################################
    # once (views fields) has been changed => call method
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for record in self:
            # note: return sudo record
            if self.expected_price < 0:
                return {
                    'warning': {'title': 'warning', 'message': 'This is negative value', 'type': 'notification'},
                }

    ##################################################
    @api.constrains('bedrooms')
    def _check_bedrooms_greater_zero(self):
        for rec in self:
            if rec.bedrooms == 0:
                raise ValidationError('Please add valid number of bedrooms')

    ####### Automated Actions Task: ######
    def check_expected_selling_date(self):
        property_ids = self.search([])
        for rec in property_ids:
            if rec.expected_selling_date and rec.expected_selling_date < fields.date.today():
                rec.is_late = True

    ## Sequence #########################
    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == 'New':
            res.ref = self.env['ir.sequence'].next_by_code('property.sequence')
            return res

    ## create_history_record Function ##############################################################
    def create_history_record(self, old_state, new_state, reason):
        for rec in self:
            rec.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or "",
            })

    ###### Workflow Buttons ###############
    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'

    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.state = 'pending'

    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'

    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'

    ############  Wizard ###########################
    def open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action

    ############  Search Domain ###########################
    def action(self):
        print(self.env['property'].search([('name', '!=', 'fff')]))

    ############  PRINT XLSX REPORT ###########################
    def property_xlsx_report(self):
        return{
            'type': 'ir.actions.act_url',
            'url': f'/property/excel/report/{self.env.context.get("active_ids")}',
            'target': 'new',
        }
    # ############  CRUD OPERATIONS ###########################
    # # create Method
    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(Property, self).create(vals_list)
    #     print("Hello inside create method")
    #     return res
    #
    # # read Method
    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #
    #     res = super(Property, self)._search(
    #         domain,
    #         offset=0,
    #         limit=None,
    #         order=None,
    #         access_rights_uid=None
    #     )
    #     print("Hello inside _search")
    #     return res
    #
    # # update Method
    # def write(self, vals_list):
    #     res = super(Property, self).write(vals_list)
    #     print("Hello inside write method")
    #     return res
    #
    # # delete Method
    # def unlink(self):
    #     res = super(Property, self).unlink()
    #     print("Hello inside unlink method")
    #     return res
