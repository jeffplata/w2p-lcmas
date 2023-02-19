# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

@auth.requires_login()
def index():
    import datetime
    services = db(db.service).select()
    loans = {'date':'01/16/2023', 'type':'MCLP', 'amount':52000, 'balance':52000, 'status':'submitted'}
    tav = 100290.00
    last_cont_date = datetime.datetime(2023,1,9)
    last_cont_amt = 2045.00
    return locals()

@auth.requires_login()
def apply_for_loan():
    service_id = request.args(0)
    service = db(db.service.id==service_id).select().first()
    db.loan.service_id.default = service_id
    db.loan.member_id.default = auth.user_id

    form = SQLFORM(db.loan, fields=["principal_amount", "terms",])
    if form.process().accepted:
        redirect(URL('loan_success'))

    d = DIV(INPUT(_type="checkbox", _id="agree", value=False)," I agree to the statement of undertaking", BR(), BR(), _class="p-1")
    form[0].insert(2, d)
    return locals()

def loan_success():
    return locals()

    # ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    if request.args(0) == 'profile':
        response.view = 'default/custom_user.html'
        m_id = db(db.member_info.user_id==auth.user_id).select(db.member_info.id).first()
        if m_id:
            member = db(db.auth_user.id==auth.user_id).select('first_name', 'last_name', 'middle_name').first()
        else:
            member = db(db.auth_user.id==auth.user_id).select('first_name', 'last_name', 'middle_name').first()
        # fields = ['first_name', 'last_name', 'middle_name', 'email', 'employee_no',\
        #             'birth_date', 'gender', 'civil_status']
        # fields = ['auth_user.first_name', 'auth_user.last_name', 'auth_user.middle_name', 'auth_user.email', 'employee_no']
        # form = SQLFORM.grid(query, 
        #     fields=fields)
        form = SQLFORM.factory(**member.fields)
        if form.process().accepted:
            response.flash = "Changes accepted"
            redirect(URL('index'))

    else:
        form = auth()
    return locals()

    # this is the original, single code
    # return dict(form=auth())