{
    'name': "Real Estate",
    'version': '1.0',
    'depends': ['base','website'],
    'author': "Het Patel",
    'category': 'Category',
    'description': "It is real estate app",
    'data': [
        'security/ir.model.access.csv',
        'security/estate_property_security.xml',
        'views/estate_property_views.xml',
        'views/my_property.xml',
        'views/estate_menus.xml',
        'views/inherited_user_view.xml',
        'views/inherited_partner_view.xml',
        'views/property_offer_wizard.xml',
        'views/estate_property_template.xml',
        'reports/estate_property_reports.xml',
        'reports/estate_property_templates.xml',
        'data/property_template.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license':'LGPL-3'
}