# -*- coding: utf-8 -*-
# try something like
def record_pages():
    return dict(page=request.args(0))

@auth.requires_login()
def record_dash_cards():
    pending_requests = db(db.member_info_update_request.status=='pending').count()
    total_requests = db(db.member_info_update_request).count()
    pending_sr_requests = db(db.service_record.status=='pending').count()
    total_sr_requests = db(db.service_record.status).count()
    role_member_id = db(db.auth_group.role=='member').select('id').first().id
    total_members = len(db(db.auth_membership.group_id==role_member_id).select(groupby=(db.auth_membership.user_id,db.auth_membership.group_id)))
    total_non_members = db(db.auth_user).count() - total_members
    return locals()

@auth.requires_login()
def record_users():
    grid = SQLFORM.grid(db.auth_user, fields=[db.auth_user.first_name, db.auth_user.last_name, db.auth_user.middle_name,
        db.auth_user.employee_no, db.auth_user.email], orderby=[db.auth_user.last_name|db.auth_user.first_name],
        create=True, formname='grid_user', deletable=False, csv=False)
    return locals()

@auth.requires_login()
def record_change_request():
    # list member info update requests
    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('record_change_request'), cid=request.cid, _class='btn btn-secondary')
    _btn_approve = A(SPAN('Approve', _class='font-weight-bold'), 
                    _href=URL('record_change_request', args=['approve', request.args(1), request.args(2)], user_signature=True), 
                    _class='btn btn-secondary', cid=request.cid )
    _btn_disapprove =  A('Disapprove', _href='#', _name="disapprove_btn", _class='btn')
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('records','record_change_request', args=['view', 'member_info_update_request', r.id], user_signature=True), cid=request.cid ))

    d = None
    q = db.member_info_update_request
    table = None
    if request.args(0)=='view':
        r = db(db.member_info_update_request.id==request.args(2)).select().first()
        h = db(db.member_info_update_request_hist.request==r.id).select().first()
#todo: continue changing 
        if r.status=='pending':
            s = "margin: 0px 5px 3px 0px;"
            btns = _btn_approve, _btn_disapprove
            da_form = FORM(LABEL("Reason for disapproval:", _style=s), INPUT(_name="reason", requires=IS_NOT_EMPTY(), _class="form-control", _style=s+"width: 20em"), INPUT(_type="submit", _value="Submit", _style=s), BR(), _name="da_form", method='GET', _class="form-inline", _style="margin: 5px 0px")
        else:
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

        d = DIV(DIV(_btn_back, *btns if r.status=='pending' else '', _class='row_buttons'), _class="web2py_grid")
        buttons = d
        d = DIV(DIV(info), t)
        table = d

        return dict(table=table, form=form, buttons=buttons, has_errors=has_errors)

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
    grid[0].insert(2, SPAN(' | ' ) + A(btn_val, _href=URL("records","record_change_request", args=filter_args, user_signature=True), 
        _id="filter_button",_class="btn btn-secondary", _style="margin-top: 7px; line-height:20px", cid=request.cid))
    return dict(grid=grid, form=d, has_errors='False')

@auth.requires_login()
def record_change_sr_request():
    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('record_change_sr_request'), cid=request.cid, _class='btn btn-secondary')
    _btn_approve = A(SPAN('Approve', _class='font-weight-bold'), 
                    _href=URL('record_change_sr_request', args=['approve', request.args(1), request.args(2)], user_signature=True), 
                    _class='btn btn-secondary', cid=request.cid )
    # _btn_disapprove =  A('Disapprove', _href=URL('record_change_sr_request', args=['disapprove', request.args(1), request.args(2)], user_signature=True), _class='btn', cid=request.cid)
    _btn_disapprove =  A('Disapprove', _href='#', _name="disapprove_btn", _class='btn')
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('records','record_change_sr_request', args=['view', 'service_record', r.id], user_signature=True), cid=request.cid ))

    table = None
    if request.args(0)=='view':
        this_id = request.args(2)
        sr_dep = db(db.service_record.id==this_id).select(join=db.department.on(db.department.id==db.service_record.department_id)).first()
        p_id = db((db.service_record.status!='pending') & (db.service_record.id!=this_id)).select().first()
        member = db.auth_user(sr_dep.service_record.user_id)
        if p_id:
            p_id = p_id['id']
            prev_sr_dep = db(db.service_record.id==p_id).select(join=db.department.on(db.department.id==db.service_record.department_id)).first()
            prev_sr_dep = [prev_sr_dep.service_record.date_effective, prev_sr_dep.department.name, prev_sr_dep.service_record.mem_position, 
                           prev_sr_dep.service_record.salary]
            bg = [prev_sr_dep[0] != sr_dep.service_record.date_effective,
                  prev_sr_dep[1] != sr_dep.department.name,
                  prev_sr_dep[2] != sr_dep.service_record.mem_position,
                  prev_sr_dep[3] != sr_dep.service_record.salary]
        else:
            prev_sr_dep = ['','','',0]
            bg = [False]*4

        bgc = 'bg-info text-white'
        t = TABLE(_class='table table-striped table-responsive')
        t.append(THEAD(TR(['', 'Last SR Values', 'New Values']), _style="font-weight:700"))
        t.append(TR(B('Date Effective'), prev_sr_dep[0], TD(sr_dep.service_record.date_effective, _class=bgc if bg[0] else '')))
        t.append(TR(B('Department'), prev_sr_dep[1], TD(sr_dep.department.name, _class=bgc if bg[1] else '')))
        t.append(TR(B('Position'), prev_sr_dep[2], TD(sr_dep.service_record.mem_position, _class=bgc if bg[2] else '')))
        t.append(TR(B('Salary'), "{:,.2f}".format(prev_sr_dep[3]), TD("{:,.2f}".format(sr_dep.service_record.salary), _class=bgc if bg[3] else '')))

        btns = ''
        info = ''
        da_form = ''
        sr = sr_dep.service_record
        if sr.status=='pending':
            s = "margin: 0px 5px 3px 0px;"
            btns = _btn_approve, _btn_disapprove
            da_form = FORM(LABEL("Reason for disapproval:", _style=s), INPUT(_name="reason", requires=IS_NOT_EMPTY(), _class="form-control", _style=s+"width: 20em"), INPUT(_type="submit", _value="Submit", _style=s), BR(), _name="da_form", method='GET', _class="form-inline", _style="margin: 5px 0px")
        else:
            if sr.status=='approved':
                info = SPAN(' Approved ', _class='text-success')
            elif sr.status=='disapproved':
                info = SPAN(' Disapproved ', _class='text-danger')
            elif sr.status=='system':
                info = SPAN(' System-generated ')

            mes = ''
            mb = db.auth_user(sr.modified_by)
            if mb:
                mes = '%s by %s. %s' % (sr.modified_on.strftime('%m/%d/%Y'), mb.first_name + ' ' + mb.last_name, 'Reason: '+sr.reason if sr.status=='disapproved' else '')
            info = DIV(info, mes, _class='border border-info rounded p-3')

        d = DIV(DIV(_btn_back, *btns if sr.status=='pending' else '', _class='row_buttons'), _class="web2py_grid")
        buttons = d
        # d = DIV(info, _class='web2py_grid' )
        d = DIV(DIV(info), DIV(B('Member: '), member.first_name+' '+member.last_name, _class='p-2', _style='background: #eaeaea'), t)

        table = d
        form = da_form

        has_errors = 'False'
        if form:
            if form.process().accepted:
                session.flash=''
                session.disapprove_reason = form.vars['reason']
                redirect(URL('record_change_sr_request', args=['disapprove', request.args(1), request.args(2) ], user_signature=True))
            elif form.errors:
                has_errors = 'True'
            else:
                session.flash=''

        return dict(table=table, form=form, buttons=buttons, has_errors=has_errors)

    elif request.args(0)=='approve':
        r = db.service_record(request.args(2)) or HTTP(400)
        r.update_record(status='approved', reason='')

    elif request.args(0)=='disapprove':
        r = db.service_record(request.args(2)) or HTTP(400)
        r.update_record(status='disapproved', reason=session.disapprove_reason)
        del session.disapprove_reason

    elif request.args(0)=='filter_pending':
        session.pending_sr_requests_only = True

    elif request.args(0)=='filter_all':
        session.pending_sr_requests_only = False

    q = None
    if session.pending_sr_requests_only:
        q = db(db.service_record.status=='pending')
        btn_val = "All requests"
        filter_args = "filter_all"
    else:
        q = db.service_record
        btn_val = "Pending requests only"
        filter_args = "filter_pending"

    grid = SQLFORM.grid(q, create=False, formname='grid_sr', deletable=False, csv=False, editable=False, details=False, links=[link1],
        orderby=~db.service_record.id)
    grid[0].insert(2, SPAN(' | ' ) + A(btn_val, _href=URL("records","record_change_sr_request", args=filter_args, user_signature=True), 
        _id="filter_button", _class="btn btn-secondary", _style="margin-top: 7px; line-height:20px", cid=request.cid))

    return dict(grid=grid, has_errors='False')
