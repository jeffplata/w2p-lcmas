# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

from gluon.tools import prettydate

@auth.requires_login()
def index():
    return locals()

@auth.requires_login()
def member_dash():
    import datetime
    services = db(db.service).select()
    loans = {'date':'01/16/2023', 'type':'MCLP', 'amount':52000, 'balance':52000, 'status':'submitted'}
    tav = 100290.00
    last_cont_date = datetime.datetime(2023,1,9)
    last_cont_amt = 2045.00
    return locals()

_btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
    ' Back', _href=URL('record_dash'), cid=request.cid, _class='btn btn-secondary')
_btn_approve = A(SPAN('Approve', _class='font-weight-bold'), 
                _href=URL('record_dash', args=['approve', request.args(1), request.args(2)], user_signature=True), 
                _class='btn btn-secondary', cid=request.cid )
_btn_disapprove =  A('Disapprove', _href='#', _class='btn', cid=request.cid)

@auth.requires_login()
def record_dash():
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('default','record_dash', args=['view', 'member_info_update_request', r.id], user_signature=True), cid=request.cid ))
    d = None
    if request.args(0)=='view':
        r = db(db.member_info_update_request.id==request.args(2)).select().first()
        m = db.auth_user(r.user_id)
        p = db.member_info(db.member_info.user_id==r.user_id)
        f = 'first_name;last_name;middle_name;employee_no' 
        t = TABLE(_class='table table-striped table-responsive')
        t.append(THEAD(TR(['', 'Original', 'New Value']), _style="font-weight:600"))
        for i in f.split(';'):
            bg = 'bg-info text-white' if (m[i] != r[i]) else ''
            t.append(TR(TD(i.capitalize().replace('_',' '), _class='font-weight-bold'), m[i], TD(r[i], _class=bg)))
        if p:
            f = 'birth_date;gender;civil_status;date_membership;entrance_to_duty'
            for i in f.split(';'):
                bg = 'bg-info text-white' if (p[i] != r[i]) else ''
                t.append(TR(TD(i.capitalize().replace('_',' '), _class='font-weight-bold'), p[i], TD(r[i], _class=bg)))
        if r.status=='pending': 
            btns = _btn_approve, _btn_disapprove
            info = ''
        else: 
            btns = ''
            info = DIV(' Approved', _class='text-success') if r.status=='approved' else DIV(' Disapproved', _class='text-danger')

        d = DIV(_btn_back, *btns if r.status=='pending' else '', _class='form_header row_buttons')
        d = DIV(d, info, _class='web2py_grid' )
        d = DIV(d, t)
    elif request.args(0)=='approve':
        r = db(db.member_info_update_request.id==request.args(2)).select().first()
        m = db.auth_user(r.user_id)
        p = db.member_info(db.member_info.user_id==r.user_id)
        f = 'first_name;last_name;middle_name;employee_no'
        changed = False
        for i in f.split(';'):
            if m[i] != r[i]:
                m[i] = r[i]
                changed = True
        if changed: m.update_record()
        changed = False
        if p:
            f = 'birth_date;gender;civil_status;date_membership;entrance_to_duty'
            for i in f.split(';'):
                if p[i] != r[i]:
                    p[i] = r[i]
                    changed = True
            if changed: p.update_record()
        r.update_record(status='approved')

    grid = SQLFORM.grid(db.member_info_update_request, create=False, formname='grid_mem', deletable=False, csv=False, links=[link1])
    return dict(grid=grid, form=d)

@auth.requires_login()
def record_dash_sr():
    q = db.service_record.status=='pending'
    grid_sr = SQLFORM.grid(q, create=False, formname='grid_sr', deletable=False, csv=False, advanced_search=False)
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

@auth.requires_login()
def custom_profile():
    response.view = 'default/custom_user.html'
    user = db.auth_user(auth.user_id)
    m_info = db.member_info(db.member_info.user_id==auth.user_id)
    miur = db.member_info_update_request
    pending_request = miur((miur.user_id==auth.user_id ) & (miur.status=='pending'))
    fields = [db.auth_user.first_name, db.auth_user.last_name, db.auth_user.middle_name, db.auth_user.email]
    t = None
    edit_request = request.vars['edit'] == '2'
    for f in fields:
        if f.name == 'email':
            f.default = user.email
        else:
            f.default = user[f.name] if not edit_request else pending_request[f.name]
    if m_info:
        fields2 = [db.member_info.employee_no, db.member_info.birth_date, db.member_info.gender, db.member_info.civil_status,
            db.member_info.entrance_to_duty, db.member_info.date_membership]
        for f in fields2:
            f.default = m_info[f.name] if not edit_request else pending_request[f.name]
        fields += fields2

        sr_heads = ['Date', 'Position', 'Salary']
        sr_rows = db(db.service_record.user_id==auth.user_id).select(
            'date_effective', 'mem_position', 'salary')
        t = TABLE(_class='table table-sm table-striped table-responsive')
        t.append(THEAD(TR(sr_heads), _style="font-weight:600"))
        for r in sr_rows:
            t.append(TR(r.date_effective,r.mem_position,r.salary)) #"{:,.2f}".format(r.salary)))

    emails = db(db.auth_user.email != user.email)
    db.auth_user.email.requires = IS_NOT_IN_DB(emails, 'auth_user.email')
    employee_nos = db(db.auth_user.employee_no != user.employee_no)
    db.auth_user.employee_no.requires = IS_EMPTY_OR(IS_NOT_IN_DB(employee_nos, 'auth_user.employee_no'))
    old_values = {}
    readonly = False if request.vars else True
    if readonly:
        form = SQLFORM.factory(*fields, readonly=readonly)
        title = 'Profile'
        if pending_request:
            form.append(DIV("You have a pending change request. ", A("View", _href=URL("custom_profile", vars={'edit':2})) ,
                _class="border border-info rounded p-3"))
        else:
            form.append(A("Update my info", _href=URL("custom_profile", vars={'edit':1}), _class="btn btn-primary"))
    else:
        if edit_request:
            form = SQLFORM.factory(*fields, Field("Check_to_Delete", "boolean", default=False))
        else:
            form = SQLFORM.factory(*fields)
        title = 'Update my profile'
        form.element('#no_table_email')['_readonly'] = 'readonly'
        form.append(INPUT(_type='hidden', _name='user_id', _value=auth.user_id))
        form.element('#submit_record__row')[1].insert(1,A("Back", _href=URL("custom_profile"), _class="btn btn-secondary"))
        if edit_request:
            form.insert(0, DIV(f"This change request was submitted {prettydate(pending_request.date_submitted)}.",
                _class="border border-info rounded p-3"))
            form.insert(1, BR())
        for f in fields:
            old_values[f.name] = f.default
        if form.process().accepted:
            # check for form changes
            if form.vars['Check_to_Delete']:
                db(db.member_info_update_request.id==pending_request.id).delete()
                session.flash = "Change request deleted"
            else:
                change_detected = False
                for f in fields:
                    if old_values[f.name] != form.vars[f.name]: 
                        change_detected = True
                        break
                if change_detected:
                    if edit_request:
                        pending_request.update_record(**db.member_info_update_request._filter_fields(form.vars))
                        session.flash = "Change request updated"
                    else:
                        id = db.member_info_update_request.insert(**db.member_info_update_request._filter_fields(form.vars))
                        session.flash = "Change request submitted"
                else:
                    session.flash = "No change detected"
            redirect(URL('user/profile'))

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
    return dict(form=form, sr_table=t, title=title)

@auth.requires_login()
def service_record():
    no_form = True
    db.service_record.user_id.default = auth.user_id
    if db((db.service_record.user_id==auth.user_id) & (db.service_record.status=='pending')).select():
        form = DIV('New record can only be added when all pending requests have been approved.', _class="border border-info rounded p-3 responsive")
    else:
        # form = SQLFORM(db.service_record, fields=['date_effective', 'department_id', 'mem_position', 'salary'], 
        #     formstyle='').process()
        no_form = False
        db.service_record.user_id.writable = False
        db.service_record.user_id.readable = False
        db.service_record.status.writable = False
        db.service_record.status.readable = False
        form = SQLFORM.factory(db.service_record)

    departments = {}
    for x in db(db.department).select():
        departments[x.id] = x.short_name
    srt = db.service_record
    sr_rows = db(db.service_record.user_id==auth.user_id,).select(
        orderby=~db.service_record.date_effective|~db.service_record.id)
    t = TABLE(_class='table table-sm table-striped table-responsive')
    t.append(THEAD(TR(['Date', 'Department', 'Position', 'Salary', 'status', '']), _style="font-weight:600"))
    for r in sr_rows:
        t.append(TR(r.date_effective, departments[r.department_id], r.mem_position, "{:,.2f}".format(r.salary), 
            TD(r.status, _class="text-muted font-italic"),
            TD(A("Delete", callback=URL("service_record_del_request", vars={'id':r.id}), delete='tr') if r.status=='pending' else ''))
        )

    if not no_form:
        if form.process().accepted:
            db.service_record.insert(**db.service_record._filter_fields(form.vars))
            redirect(URL('service_record'))

    return dict(form=form, table=t)

@auth.requires_login()
def service_record_del_request():
    # member deletes their own pending request
    id = request.vars.id
    if not db(db.service_record.id==id).delete():
        raise HTTP(400)
    else:
        response.js = "web2py_component('%s', '%s');" % (URL('service_record'), 'service_record_div')

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
            title = forms['title']
        else:
            redirect(URL('index'))
    else:
        form = auth()
    return locals()

    # this is the original, single code
    # return dict(form=auth())