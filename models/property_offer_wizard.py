from odoo import _, api, fields, models


class OfferWizard(models.TransientModel):
    _name = 'property.offer.wizard'

    offer_price = fields.Float(default=0)
    offer_partner = fields.Many2one('res.partner',required=True)

    def send_offer_action(self):
        self.ensure_one()
        activeIds = self.env.context.get('active_ids')
        #print("######################################",self.offer_partner)
        for x in activeIds:
            self.env['estate.property.offer'].create({'price': self.offer_price,'partner_id':self.offer_partner.id,'property_id':x})
        return True