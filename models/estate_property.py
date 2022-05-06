from email.policy import default
from odoo import api,fields, models
from odoo.exceptions import UserError, ValidationError

from datetime import datetime, timedelta

## property type --model
class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "estate properties type"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property','property_type_id')

## property offer --model
class EstateProperyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "estate properties offers"
    _order = "price desc"

    @api.depends("validity")
    def _compute_date_deadline(self):
        #print("Recordset data -->",self,"\nDetailed data-->",self[0],"\nRecord price -->",self[0].price)
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
    
    @api.model
    def create(self, vals):
        new_offer = super(EstateProperyOffer, self).create(vals)
        for record in new_offer:
            record.property_id.state='offer received'
            print('###############################',record.property_id.state)
        return new_offer
    
    def _inverse_date_deadline(self):
        #print("Recordset data",self)
        for record in self: 
            record.validity = int((record.date_deadline - (record.create_date).date()).days)

    def action_accepted(self):
        for record in self:
            #if record.status =='':
            #    raise UserError("Cancel property cannot be sold")
            record.status='accepted'
            record.property_id.selling_price=record.price
            record.property_id.buyer_id=record.partner_id
            record.property_id.state = 'offer accepted'
    
    def action_refused(self):
        for record in self:
            #if record.status =='sold':
            #    raise UserError("Sold property cannot be cancel")
            record.status='refused'


    @api.constrains('property_id.selling_price')
    def check_selling_price(self):
        for record in self:
            if record.price < (0.9*record.property_id.expected_price):
                raise ValidationError("Selling price must be more than 90% of expected price")

    price = fields.Float(default=0)
    status = fields.Selection(selection=[('accepted','Accepted'),('refused','Refused')], copy=False)
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',required=True)

    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    validity = fields.Integer()
    active = fields.Boolean(default=True)
    confirm_token = fields.Integer()
    prop_state = fields.Selection(related='property_id.state')

    #_sql_constraints = []

## property tag --model
class EstateProperyTag(models.Model):
    _name = "estate.property.tag"
    _description = "estate properties tags"
    _order = "name"
    
    name = fields.Char(required=True)

class EstatePropertyImages(models.Model):
    _name = "estate.property.images"
    _description = "estate properties images"

    property_id = fields.Many2one('estate.property')
    image = fields.Binary()

## property --model
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "estate properties model"
    _order = "id desc"
    
    ## total area --compute field call method
    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    # best price --compute field call method
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
    
    # garden --onchange method
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden == True:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = None
            self.garden_orientation = None

    """
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price == 0:# and record.offer_ids.price <= (0.9*record.expected_price):
                recordset0 = record.offer_ids
                for record0 in recordset0:
                    if record == record0.property_id:
                        if record0.price<=(0.9*record.expected_price):
                            raise ValidationError("Selling price must be more than 90% of expected price")
    """
    def _get_description(self):
        if self.env.context.get('is_my_property'):
            return self.env.user.name + "'s Property"

    name = fields.Char(string='Title', required=True)
    property_type_id = fields.Many2one('estate.property.type')
    description = fields.Text(default=_get_description)
    #image = fields.Binary()
    image_ids = fields.One2many('estate.property.images','property_id')
    postcode = fields.Char()
    date_availability = fields.Date(string='Available from', default=fields.Date.today(), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms =fields.Integer(default=1)
    bathrooms =fields.Integer(default=1)
    kitchen =fields.Integer(default=1)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(selection=[('north', 'North'), ('south', 'South'), ('east','East'), ('west','West')])
    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[('publish pending','Publish Pending'),('new','New'),('offer received','Offer Received'),('offer accepted','Offer Accepted'),('sold','Sold'),('canceled','Canceled')], required=True, default='new', copy=False)

    seller_id = fields.Many2one('res.partner',copy=False)
    buyer_id = fields.Many2one('res.partner',copy=False)   
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag')
    offer_ids = fields.One2many('estate.property.offer','property_id')

    total_area = fields.Float(compute="_compute_total_area")

    best_price = fields.Float(compute="_compute_best_price")

    status = fields.Char(copy=False, default='new')
    
    def action_sold(self):
        for record in self:
            if record.status =='cancel':
                raise UserError("Cancel property cannot be sold")
            record.status='sold'
            record.state='sold'
    
    def action_cancel(self):
        for record in self:
            if record.status =='sold':
                raise UserError("Sold property cannot be cancel")
            record.status='cancel'
            record.state='canceled'

    def open_offer(self):
        print("#############################################",self.id)
        return {
            "type" : "ir.actions.act_window",
            "res_model" : "estate.property.offer",
            "views":[[False,'tree']],
            "target":"new",
            "domain":[('status','=','accepted'),('property_id','=',self.id)]
        }

    def _state_changed_mail(self):
        template_obj = self.env['mail.template'].sudo().search([('name','=','state change email')], limit=1)
        receipt_list = [record.seller_id.email for record in self]
        print("###########################",receipt_list)
        body = template_obj.body_html
        body=body.replace('--seller_name--',self.seller_id.name)
        body=body.replace('--state_changed_to--',self.state)
        if template_obj:
            mail_values = {
                'subject': template_obj.subject,
                'body_html': body,
                'email_to':';'.join(map(lambda x: x, receipt_list)),
                'email_from': template_obj.email_from,
            }
        return self.env['mail.mail'].create(mail_values).send()
    
    def assign_to_me(self):
        for record in self:
            if record.salesperson_id.id == False:
                record.salesperson_id = self.env.user
        
        create_and_send_email = self._state_changed_mail()
    
    def publish_property(self):
        for record in self:
            if record.state == 'publish pending':
                record.state = 'new'

    #_sql_constraints = [
    #    ('check_expected_price', 'CHECK(expected_price >= 0)', 'Expected price must not be negative.'),
    #    ('check_selling_price', 'CHECK(selling_price >= 0)', 'Selling price must not be negative.'),

    #]