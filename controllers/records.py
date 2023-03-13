# -*- coding: utf-8 -*-
# try something like
_btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
    ' Back', _href=URL('record_dash'), cid=request.cid, _class='btn btn-secondary')
_btn_approve = A(SPAN('Approve', _class='font-weight-bold'), 
                _href=URL('record_dash', args=['approve', request.args(1), request.args(2)], user_signature=True), 
                _class='btn btn-secondary', cid=request.cid )
_btn_disapprove =  A('Disapprove', _href='#', _class='btn', cid=request.cid)

def record_member_update():
    return dict(page=request.args(0))

@auth.requires_login()
def record_dash_main():
    pending_requests = db(db.member_info_update_request.status=='pending').count()
    total_requests = db(db.member_info_update_request).count()
    pending_sr_requests = db(db.service_record.status=='pending').count()
    total_sr_requests = db(db.service_record.status).count()
    role_member_id = db(db.auth_group.role=='member').select('id').first().id
    total_members = len(db(db.auth_membership.group_id==role_member_id).select(groupby=(db.auth_membership.user_id,db.auth_membership.group_id)))
    total_non_members = db(db.auth_user).count() - total_members
    return locals()

@auth.requires_login()
def record_dash_users():
    grid = SQLFORM.grid(db.auth_user, fields=[db.auth_user.first_name, db.auth_user.last_name, db.auth_user.middle_name,
        db.auth_user.employee_no, db.auth_user.email], orderby=[db.auth_user.last_name|db.auth_user.first_name],
        create=True, formname='grid_user', deletable=False, csv=False)
    return locals()

@auth.requires_login()
def record_dash():
    # list member info update requests
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('records','record_dash', args=['view', 'member_info_update_request', r.id], user_signature=True), cid=request.cid ))
    d = None
    q = db.member_info_update_request
    if request.args(0)=='view':
        r = db(db.member_info_update_request.id==request.args(2)).select().first()
        h = db(db.member_info_update_request_hist.request==r.id).select().first()

        if r.status=='approved':
            if not h:
                h = {}
                f = 'first_name;last_name;middle_name;employee_no;birth_date;gender;civil_status;date_membership;entrance_to_duty'
                for i in f.split(';'):
                    h[i] = 'no record'
            m = p = h
        else: #pending
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
            mb = db.auth_user(r.modified_by)
            mes = ''
            if mb: 
                mes = '%s by %s' % (r.modified_on.strftime('%m/%d/%Y'), mb.first_name + ' ' + mb.last_name)
            info = DIV(SPAN(' Approved ', _class='text-success') if r.status=='approved' else SPAN(' Disapproved ', _class='text-danger'), 
                mes, _class='border border-info rounded p-3') 

        d = DIV(_btn_back, *btns if r.status=='pending' else '', _class='form_header row_buttons')
        d = DIV(d, info, _class='web2py_grid' )
        d = DIV(d, t)
    elif request.args(0)=='approve':
        h = {}
        r = db(db.member_info_update_request.id==request.args(2)).select().first()
        m = db.auth_user(r.user_id)
        p = db.member_info(db.member_info.user_id==r.user_id)
        f = 'first_name;last_name;middle_name;employee_no'
        h['request'] = r.id
        h['user_id'] = r.user_id
        changed = False
        for i in f.split(';'):
            h[i] = m[i]
            if m[i] != r[i]:
                m[i] = r[i]
                changed = True
        if changed: m.update_record()
        changed = False
        if p:
            f = 'birth_date;gender;civil_status;date_membership;entrance_to_duty'
            for i in f.split(';'):
                h[i] = p[i]
                if p[i] != r[i]:
                    p[i] = r[i]
                    changed = True
            if changed: p.update_record()
        if not db(db.member_info_update_request_hist.request==r.id).select():
            db.member_info_update_request_hist.insert(**h)
        r.update_record(status='approved')
    elif request.args(0)=='filter_pending':
        session.pending_requests_only = True
    elif request.args(0)=='filter_all':
        session.pending_requests_only = False

    if session.pending_requests_only:
        q = db(db.member_info_update_request.status=='pending')
        btn_val = "All requests"
        filter_args = "filter_all"
    else:
        btn_val = "Pending requests only"
        filter_args = "filter_pending"
    grid = SQLFORM.grid(q, orderby=~db.member_info_update_request.id,
        create=False, formname='grid_mem', deletable=False, csv=False, links=[link1], details=False, editable=False)
    grid[0].insert(2, SPAN(' | ' ) + A(btn_val, _href=URL("records","record_dash", args=filter_args, user_signature=True), 
        _id="filter_button",_class="btn btn-secondary", _style="margin-top: 7px; line-height:20px", cid=request.cid))
    return dict(grid=grid, form=d)

@auth.requires_login()
def record_dash_sr():
    q = db.service_record.status=='pending'
    grid_sr = SQLFORM.grid(q, create=False, formname='grid_sr', deletable=False, csv=False, advanced_search=False)
    return locals()
