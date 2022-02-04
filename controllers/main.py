from odoo import http
from odoo.http import request

class RealEstateController(http.Controller):

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
                'properties': request.env['estate.property'].sudo().search([], limit=8)
            })

    @http.route(['/property/<model("estate.property"):property>', '/property/<string:is_static>'], auth="public", website=True)
    def property_details(self, property=False, **kw):
        if property:
            return request.render('Real_estate.property_details', {
                'property': property,
            })