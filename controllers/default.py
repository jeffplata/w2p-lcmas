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

def custom_profile():
    response.view = 'default/custom_user.html'
    user = db.auth_user(auth.user_id)
    m_info = db.member_info(db.member_info.user_id==auth.user_id)
    fields = [db.auth_user.first_name, db.auth_user.last_name, db.auth_user.middle_name, db.auth_user.email, db.auth_user.employee_no]
    for f in fields:
        f.default = user[f.name]
    if m_info:
        fields2 = [db.member_info.birth_date, db.member_info.gender, db.member_info.civil_status]
        for f in fields2:
            f.default = m_info[f.name]
        fields += fields2

    form = SQLFORM.factory(*fields, readonly=True)
    # ... this code only works for editing
    # for f in db.auth_user:
    #     form.vars[f.name] = user[f.name]
    # if m_info:
    #     for f in db.member_info:
    #         form.vars[f.name] = m_info[f.name]
    # form.element('#no_table_email')['_readonly'] = 'readonly'

    # if form.process().accepted:
    #     response.flash = "Changes accepted"
    #     redirect(URL('index'))
    sr_heads = ['Date', 'Position', 'Salary']
    sr_rows = db(db.service_record.user_id==auth.user_id).select(
        'date_effective', 'mem_position', 'salary')
    t = TABLE(_class='table table-sm table-striped table-responsive')
    t.append(THEAD(TR(sr_heads), _style="font-weight:600"))
    for r in sr_rows:
        t.append(TR(r.date_effective,r.mem_position,"{:,.2f}".format(r.salary)))

    return dict(form=form, sr_table=t)


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
        if auth.is_logged_in():
            forms = custom_profile()
            form = forms['form']
            sr_table = forms['sr_table']
        else:
            redirect(URL('index'))
    else:
        form = auth()
    return locals()

    # this is the original, single code
    # return dict(form=auth())