{
    'name': "real_estate",
    'version': '1.0',
    'summary': 'Real Estate',
    'author': "UNLA-GrupoM",
    'depends': ['base'],
    'data': [
        'security/ir.model.category.xml',
        'security/real_estate_res_groups.xml',
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/real_estate_menuitem.xml',
    ],
    'installable': True,
    'application': True,
}