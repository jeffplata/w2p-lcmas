# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# ----------------------------------------------------------------------------------------------------------------------
# this is the main application menu add/remove items as required
# ----------------------------------------------------------------------------------------------------------------------

m = (T('Library'), False, None, [ ])

if auth.has_permission('manage', 'service', 0):
    m[3].append((T('Services'), False, URL('default', 'library.load', args=['service'], user_signature=True)))

response.menu = [
    (T('Home'), False, URL('default', 'index'), [])
]

if m[3]:
    response.menu += [m]

