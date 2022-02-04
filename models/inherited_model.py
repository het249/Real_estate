from odoo import fields, models

class InheritedModel_ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many("estate.property","salesperson_id")

class InheritedModel_ResPartner(models.Model):
    _inherit = 'res.partner'

    is_buyer = fields.Boolean('Is a buyer?')