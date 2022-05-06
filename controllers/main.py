from odoo import http
import json
import random
import base64
from odoo.http import request, Response

class RealEstateController(http.Controller):

    def _offer_confirm_token_mail(self, request0, new_res_partner, new_offer, confirm_token):
        template_obj = request0.env['mail.template'].sudo().search([('name','=','offer confirm token email')], limit=1)
        receipt_list = [new_res_partner.email]
        print("###########################",receipt_list)
        body = template_obj.body_html
        confirm_token_link = "localhost:8069/offer_confirm_token/offer="+str(new_offer.id)+"&token="+str(confirm_token)
        body=body.replace('--confirm-token-link--',confirm_token_link)
        if template_obj:
            mail_values = {
                'subject': template_obj.subject,
                'body_html': body,
                'email_to':';'.join(map(lambda x: x, receipt_list)),
                'email_from': template_obj.email_from,
            }
        return request0.env['mail.mail'].create(mail_values).send()

    @http.route('/hello', auth="public")
    def hello(self, **kw):
        return "welcome to real estate website."

    @http.route('/hello_user', auth="user")
    def hello_user(self, **kw):
        return "Hello %s, welcome to real estate website." %(request.env.user.name)

    @http.route('/hello_template')
    def hello_template(self, **kw):
        return request.render('Real_estate.static_template')

    @http.route('/hello_template_user',website=True)
    def hello_template_user(self, **kw):
        properties = request.env['estate.property'].search([])
        print ("properties ::: ", properties)
        return request.render('Real_estate.hello_template_user', { 'user': request.env.user, 'properties': properties })

    @http.route(['/property', '/property/static/<string:is_static>'], auth="public", website=True)
    def properties(self, is_static=False, **kw):
        if is_static:
            return request.render('Real_estate.static_template')
        return request.render('Real_estate.hello_template_user', {
                'user': request.env.user,
                'properties': request.env['estate.property'].sudo().search([])
            })

    @http.route(['/property/<model("estate.property"):property>', '/property/<string:is_static>'], auth="public", website=True)
    def property_details(self, property=False, **kw):
        if property:
            return request.render('Real_estate.property_details', {
                'property': property,
            })
    
    @http.route(['/publish_property'], auth="public", website=True)
    def publish_property(self, **kw):
        return request.render('Real_estate.publish_property_template')

    @http.route(['/offer_confirm_mail/<model("estate.property"):property0>'], auth="public", csrf=False, website=True)
    def offer_confirm_mail(self, property0=False, **kw):
        offerer_name = "Het offering"
        offerer_email = kw.get("email")
        offer_price = int(kw.get("offerPrice"))
        new_res_partner = request.env['res.partner'].sudo().search([('email','=',offerer_email)])
        if new_res_partner.id == False:
            new_res_partner = request.env['res.partner'].sudo().create({'name':offerer_name,'email':offerer_email})
        print("################################",property0)
        confirm_token = random.randint(0, 1000000000)
        data_dict = {
                'partner_id':new_res_partner.id,
                'property_id': property0.id,
                'price': offer_price,
                'active': False,
                'confirm_token': confirm_token
            }
        new_offer = request.env['estate.property.offer'].sudo().create(data_dict)
        self._offer_confirm_token_mail(request,new_res_partner,new_offer,confirm_token)
        return request.render('Real_estate.publish_property_template')
    
    @http.route(['/offer_confirm_token/<string:get_query>'], auth="public", website=True)
    def offer_confirm_token(self, get_query=False, **kw):
        print('########################',get_query)
        if get_query:
            get_query_lst = get_query.split('&')
            offer_id = get_query_lst[0].split('=')[1]
            offer_token = int(get_query_lst[1].split('=')[1])
        
        if offer_id and offer_token:
            print('########################',offer_id, offer_token)
            offer = request.env['estate.property.offer'].sudo().search([('active','=',False),('id','=',offer_id)])
            print('########################',offer.confirm_token, type(offer.confirm_token))
            if offer.confirm_token == offer_token:
                offer.active = True
        return request.render('Real_estate.publish_property_template')
    
    @http.route(['/publish_property_rpc'], auth="public", csrf=False, website=True)
    def publish_property_rpc(self, **kw):
        if request.httprequest.method == 'POST':
            seller_name = "Het Patel"
            seller_email = "aaabbc@example.com"
            seller_phone = "+91 9999999999"
            new_res_partner = request.env['res.partner'].sudo().search([('email','=',seller_email)])
            if new_res_partner.id == False:
                new_res_partner = request.env['res.partner'].sudo().create({'name':seller_name,'email':seller_email,'phone':seller_phone})

            print("####################",new_res_partner)
            data_dict = {
                'name':'from Form',
                'description':'abc',
                'expected_price':500000,
                'state':'publish pending',
                'salesperson_id': None,
                'seller_id': new_res_partner.id
            }
            new_property = request.env['estate.property'].sudo().create(data_dict)
            print("###########################",new_property)
            if 'property_images' in request.params:
                attached_files = request.httprequest.files.getlist('property_images')
                for attachment in attached_files:
                    attached_file = attachment.read()
                    request.env['estate.property.images'].sudo().create({
                                'property_id': new_property.id,
                                'image': base64.encodebytes(attached_file),
                            })
            return request.render('Real_estate.publish_property_template')