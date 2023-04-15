# -*- coding: utf-8 -*-
# try something like
def bread_crumbs(crumbs,cid=None):
    links = None
    c_len = len(crumbs)
    e = []
    if crumbs:
        links = DIV([(A(f'{k}', _href=f'{v}', cid=cid) if v else SPAN(k))+SPAN(' / ' if i+1 != c_len else '') for i, (k, v) in enumerate(crumbs.items())],
            _class='rounded p-2', _style='background: #EAEAEA; margin: 5px 0;')
    return links


def record_pages():
    return dict(page=request.args(0))


def user_service_record():
    user = db.auth_user(request.vars['user_id'])
    title = f'Service record of {user.first_name} {user.last_name}'
    crumbs = bread_crumbs(
        {'User list':URL('records', 'record_users', args=session.grid_query or None, user_signature=True),
         user.first_name+' '+user.last_name:'',
         'Service record':''
        }, 
        request.cid)
    query = db.service_record.user_id == user.id
    db.service_record.user_id.default = user.id
    fields = 'date_effective,department_id,mem_position,salary,status'
    grid = SQLFORM.grid(query, formname='grid_user_service_record', csv=False, searchable=False, deletable=False,
        fields=[db.service_record[i] for i in fields.split(',')],
        createargs=dict(submit_button='Add service record'),
        formargs=dict(fields=[i for i in fields.split(',')[:-1]])
        )
    return locals()

@auth.requires_login()
def record_dash_cards():
    pending_requests = db(db.member_info_update_request.status=='pending').count()
    total_requests = db(db.member_info_update_request).count()
    pending_sr_requests = db(db.service_record.status=='pending').count()
    total_sr_requests = db(db.service_record.status).count()
    total_members = len(db(db.auth_membership.group_id==auth.id_group('member')).select(groupby=(db.auth_membership.user_id,db.auth_membership.group_id)))
    total_non_members = db(db.auth_user).count() - total_members
    return locals()


def get_member_salary(member_id):
    r = db((db.service_record.user_id==member_id) & (db.service_record.status!='pending')).\
            select(db.service_record.salary, orderby=~db.service_record.id).first()
    return moneytize(r['salary']) if r else ''

# users/view
# users/update
# users/group
@auth.requires_login()
def record_users():
    # args(0) = action
    # args(1) = table
    # args(2) = id

    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('record_users', args=session.grid_query if session.grid_query else None, user_signature=True), 
        cid=request.cid, _class='btn btn-secondary')

    fields = fld_user = [db.auth_user.first_name, db.auth_user.last_name, db.auth_user.middle_name,
        db.auth_user.employee_no, db.auth_user.email]
    fld_profile = [db.member_info.birth_date, db.member_info.gender, db.member_info.civil_status, db.member_info.date_membership, db.member_info.entrance_to_duty]
    
    if request.args(0) == 'edit':
        title = 'Edit user %s' % request.args(2)
        user = db.auth_user(request.args(2))
        if user:
            for f in fld_user:
                f.default = user[f.name]
            profile = db.member_info(db.member_info.user_id==user.id)
            if profile:
                for f in fld_profile:
                    f.default = profile[f.name]
                fields += fld_profile

            old_values = {}
            for f in fields:
                old_values[f.name] = f.default

            emails = db(db.auth_user.email != user.email)
            db.auth_user.email.requires = IS_NOT_IN_DB(emails, 'auth_user.email')
            employee_nos = db(db.auth_user.employee_no != user.employee_no)
            db.auth_user.employee_no.requires = IS_EMPTY_OR(IS_NOT_IN_DB(employee_nos, 'auth_user.employee_no'))
            if db( (db.auth_membership.user_id == user.id) &
                   (db.auth_membership.group_id == auth.id_group('member')) ).select():
                db.auth_user.employee_no.requires = IS_NOT_IN_DB(employee_nos, 'auth_user.employee_no')

            form = SQLFORM.factory(*fields, readonly=False)
            # form.insert(0, DIV(DIV(_btn_back, _class='row_buttons'), _class="web2py_grid") )
            form.element('#submit_record__row')[1].insert(1, _btn_back)
            form.element('#no_table_email')['_readonly'] = 'readonly'

            if form.process().accepted:
                change_detected = False
                for f in fld_user:
                    if old_values[f.name] != form.vars[f.name]:
                        change_detected = True
                        break
                if change_detected:
                    user.update_record(**db.auth_user._filter_fields(form.vars))

                # log changes to member_info_update_request/_hist
                id = db.member_info_update_request.insert(**db.member_info_update_request._filter_fields(form.vars))
                r = db.member_info_update_request(id)
                r.update_record(user_id=user.id, status='approved')
                old_values.update({'request':id, 'date_submitted': r.date_submitted})
                id = db.member_info_update_request_hist.insert(**db.member_info_update_request_hist._filter_fields(old_values))
                r = db.member_info_update_request_hist(id)
                r.update_record(user_id=user.id)

                if profile:
                    change_detected = False
                    for f in fld_profile+[db.member_info.employee_no]:
                        if old_values[f.name] != form.vars[f.name]:
                            change_detected = True
                            break
                    if change_detected:
                        profile.update_record(**db.member_info._filter_fields(form.vars))
                # todo: let member view change history in profile
                redirect(URL('records', 'record_users'))

            return dict(form=form, title=title)

        else:
            HTTP(400)

    elif request.args(0) == 'new_user':
        title = 'New user'
        fields += [db.auth_user.password]
        db.auth_user.password.readable = False
        db.auth_user.password.writable = False
        db.auth_user.password.default = db.auth_user.password.requires[0]('Password1')[0]
        form = SQLFORM.factory(*fields)
        form.element('#submit_record__row')[1].insert(1, _btn_back)

        if form.process().accepted:
            db.auth_user.validate_and_insert(**db.auth_user._filter_fields(form.vars))
            session.flash = 'New user added.'
            redirect(URL('records', 'record_users', args=['new_user', request.args(1)], user_signature=True))

        return dict(form=form, title=title)

    elif request.args(0) == 'new_member':
        title = 'New member'
        allfields = fields + fld_profile + [db.auth_user.password]
        db.auth_user.password.readable = False
        db.auth_user.password.writable = False
        db.auth_user.password.default = db.auth_user.password.requires[0]('Password1')[0]
        db.auth_user.employee_no.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'auth_user.employee_no')]
        form = SQLFORM.factory(*allfields)
        form.element('#submit_record__row')[1].insert(1, _btn_back)

        if form.process().accepted:
            id = db.auth_user.insert(**db.auth_user._filter_fields(form.vars))
            form.vars.user_id = id
            db.member_info.insert(**db.member_info._filter_fields(form.vars))
            group_id = db.auth_group(role='member')['id']
            db.auth_membership.validate_and_insert(user_id=id, group_id=group_id)
            session.flash = 'New member added.'
            redirect(URL('records', 'record_users', args=['new_member', request.args(1)], user_signature=True))

        return dict(form=form, title=title)

    elif request.args(0) == 'group':
        user = db.auth_user(request.args(2))
        title = 'Assign user %s to group' % (user.first_name + ' ' + user.last_name)
        groups = db( db.auth_membership.user_id == user.id )
        _link = [ dict(header='', body=lambda r: A('Delete', _class='button btn btn-default btn-secondary', 
                _href=URL('records','record_users', args=['delete', 'auth_membership', r.id], user_signature=True), cid=request.cid )) ]

        grid = SQLFORM.grid(groups, formname='grid_user_group', details=False, create=False, csv=False, paginate=10, 
            searchable=False, editable=False, deletable=False, links=_link)

        user_groups = db(db.auth_membership.user_id==user.id).select()
        ug = [g.group_id for g in user_groups]
        group_options = db(~db.auth_group.id.belongs(ug))
        db.auth_membership.group_id.requires = IS_IN_DB(group_options, 'auth_group.id', '%(role)s (%(id)s)', zero=None)
        form = SQLFORM(db.auth_membership, fields=['group_id'], submit_button='Assign group', formname='form_group_add')

        if form.process(dbio=False).accepted:
            gid = form.vars['group_id']
            fv = {'group_id':gid, 'user_id':user.id}
            db.auth_membership.insert(**fv)
            redirect(URL('records', 'record_users', args=['group', request.args(1), request.args(2)], user_signature=True))

        return dict(grid=grid, form=form, title=title, button=_btn_back)

    elif request.args(0) == 'delete':
        if request.args(1) == 'auth_membership':
            memb_q = db.auth_membership.id==request.args(2)
            user_id = db(memb_q).select(db.auth_membership.user_id).first().user_id
            db(memb_q).delete()

            redirect(URL('records', 'record_users', args=['group', request.args(1), user_id], user_signature=True))

    else:
        title = 'User list'
        query = db.auth_user
        if request.args(0) == 'list_non_members':
            title += ' [non members]'

            m_g_id = auth.id_group('member')
            qm = db(db.auth_membership.group_id==m_g_id)._select(db.auth_membership.user_id)
            query = ~db.auth_user.id.belongs(qm)

        elif request.args(0) == 'list_group':
            title += f' [group: {request.args(2)}]'
            query = (db.auth_membership.group_id==request.args(1))&(db.auth_user.id==db.auth_membership.user_id)

        _btn_add_user = A(SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), ' Add user', _href=URL('record_users', args=['new_user', 'auth_user'], user_signature=True), cid=request.cid, _class='btn btn-secondary')
        _btn_add_member = A(SPAN(_class="icon plus icon-plus glyphicon glyphicon-plus"), ' Add member', _href=URL('record_users', args=['new_member', 'auth_user'], user_signature=True), cid=request.cid, _class='btn btn-secondary')
        
        _link_sr = dict(header='', body=lambda r: A('Service Record', _class='button btn btn-default btn-secondary', 
            _href=URL('records','user_service_record.load', vars={'user_id':r.id}, user_signature=True), cid=request.cid )
            if auth.has_membership(auth.id_group('member'), r.id) else 'non-member'
            )
        _link_mbs = dict(header='Salary', body=lambda r: get_member_salary(r.id))
        link1 = [_link_mbs, _link_sr]
        if auth.has_membership('manager'):
            _link_group = dict(header='', body=lambda r: A('Group', _class='button btn btn-default btn-secondary', 
                _href=URL('records','record_users', args=['group', 'auth_user', r.id], user_signature=True), cid=request.cid ))
            link1 += [_link_group]
        # session.grid_query = [request.args(0), request.args(1), request.args(2)]
        session.grid_query = f'{request.args(0)}/{request.args(1)}/{request.args(2)}'
        grid = SQLFORM.grid(query, fields=fields, orderby=[db.auth_user.last_name|db.auth_user.first_name],
            formname='grid_user', details=False, create=False, deletable=False, csv=False, paginate=10, links=link1)
        grid.element('.web2py_console').insert(1, _btn_add_member)
        grid.element('.web2py_console').insert(1, _btn_add_user)

        return dict(grid=grid, title=title)


# record_change_request/view
# record_change_request/approve
# record_change_request/disapprove
# record_change_request/filter_pending
# record_change_request/filter_all
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
    table = None
    if request.args(0)=='view':
        # status = 'pending'
        # status = 'approved'
        # status = 'disapproved'

        # r = this request, h =  history of change requests
        r = db(db.member_info_update_request.id==request.args(2)).select().first()

        if r.status=='pending':
            # compare (r)request with current (m)member information
            # m = member info, p = corresponding member profile
            m = db.auth_user(r.user_id)
            p = db.member_info(db.member_info.user_id==r.user_id)
        else:  # approved / disapproved
            # compare (r)request with (h)request history
            h = db(db.member_info_update_request_hist.request==r.id).select().first()
            if not h:
                h = {}
                f = 'first_name;last_name;middle_name;employee_no;birth_date;gender;civil_status;date_membership;entrance_to_duty'
                for i in f.split(';'):
                    h[i] = 'no record'
            m = p = h

        # set up table of values
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

        # set up buttons, info and da-form
        btns = ''
        info = ''
        reason_form = ''
        if r.status=='pending':
            btns = _btn_approve, _btn_disapprove
            s = "margin: 0px 5px 3px 0px;"
            reason_form = FORM(LABEL("Reason for disapproval:", _style=s), INPUT(_name="reason", requires=IS_NOT_EMPTY(), _class="form-control", _style=s+"width: 20em"), INPUT(_type="submit", _value="Submit", _style=s), BR(), _name="da_form", method='GET', _class="form-inline", _style="margin: 5px 0px")
        else:
            if r.status=='approved': 
                info = SPAN(' Approved ', _class='text-success')
            elif r.status=='disapproved': 
                info = SPAN(' Disapproved ', _class='text-danger')

            mb = db.auth_user(r.modified_by)
            mes = '%s by %s. %s' % (r.modified_on.strftime('%m/%d/%Y'), mb.first_name + ' ' + mb.last_name, 'Reason: '+r.reason if r.status=='disapproved' else '') if mb else ''
            info = DIV(info, mes, _class='border border-info rounded p-3') 

        buttons = DIV(DIV(_btn_back, *btns, _class='row_buttons'), _class="web2py_grid")
        table = DIV(info, t)
        form = reason_form
        
        has_errors = 'False'
        if form:
            if form.process().accepted:
                session.disapprove_reason = form.vars['reason']
                redirect(URL('record_change_request', args=['disapprove', request.args(1), request.args(2) ], user_signature=True))
            elif form.errors:
                has_errors = 'True'
                response.flash = ''

        return dict(table=table, form=form, buttons=buttons, has_errors=has_errors)

    elif request.args(0)=='approve':
        h = {}
        # r = db(db.member_info_update_request.id==request.args(2)).select().first() or HTTP(400)
        # todo: how to reaise http 400
        r = db.member_info_update_request(request.args(2)) or HTTP(400)
        m = db.auth_user(r.user_id)
        p = db.member_info(db.member_info.user_id==r.user_id)
        f = 'first_name;last_name;middle_name;employee_no'
        h['request'] = r.id
        h['user_id'] = r.user_id
        h['date_submitted'] = r.date_submitted
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
        r.update_record(status='approved', reason='')

    elif request.args(0)=='disapprove':
        r = db.member_info_update_request(request.args(2)) or HTTP(400)
        r.update_record(status='disapproved', reason=session.disapprove_reason)
        del session.disapprove_reason

    elif request.args(0)=='filter_pending':
        session.pending_requests_only = True
    elif request.args(0)=='filter_all':
        session.pending_requests_only = False

    if session.pending_requests_only:
        q = db(db.member_info_update_request.status=='pending')
        btn_val = "All requests"
        filter_args = "filter_all"
    else:
        q = db.member_info_update_request
        btn_val = "Pending requests only"
        filter_args = "filter_pending"

    response.flash = ''
    grid = SQLFORM.grid(q, orderby=~db.member_info_update_request.id,
        create=False, formname='grid_mem', deletable=False, csv=False, links=[link1], details=False, editable=False)
    grid[0].insert(2, SPAN(' | ' ) + A(btn_val, _href=URL("records","record_change_request", args=filter_args, user_signature=True), 
        _id="filter_button",_class="btn btn-secondary", _style="margin-top: 7px; line-height:20px", cid=request.cid))
    return dict(grid=grid, has_errors='False')


@auth.requires_login()
def record_change_sr_request():
    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('record_change_sr_request'), cid=request.cid, _class='btn btn-secondary')
    _btn_approve = A(SPAN('Approve', _class='font-weight-bold'), 
                    _href=URL('record_change_sr_request', args=['approve', request.args(1), request.args(2)], user_signature=True), 
                    _class='btn btn-secondary', cid=request.cid )
    # _btn_disapprove =  A('Disapprove', _href=URL('record_change_sr_request', args=['disapprove', request.args(1), request.args(2)], user_signature=True), _class='btn', cid=request.cid)
    _btn_disapprove =  A('Disapprove', _href='#', _name="disapprove_btn", _class='btn')
    # todo: disapprove sr change request
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('records','record_change_sr_request', args=['view', 'service_record', r.id], user_signature=True), cid=request.cid ))

    table = None
    if request.args(0)=='view':
        this_id = request.args(2)
        sr_dep = db(db.service_record.id==this_id).select(join=db.department.on(db.department.id==db.service_record.department_id)).first()
        member = db.auth_user(sr_dep.service_record.user_id)
        p_id = db((db.service_record.status!='pending') & (db.service_record.id!=this_id) & (db.service_record.user_id==member.id)).select().first()
        if p_id:
            p_id = p_id['id'] # id of latest sr for this member
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
        reason_form = ''
        sr = sr_dep.service_record
        if sr.status=='pending':
            s = "margin: 0px 5px 3px 0px;"
            btns = _btn_approve, _btn_disapprove
            reason_form = FORM(LABEL("Reason for disapproval:", _style=s), INPUT(_name="reason", requires=IS_NOT_EMPTY(), _class="form-control", _style=s+"width: 20em"), INPUT(_type="submit", _value="Submit", _style=s), BR(), _name="da_form", method='GET', _class="form-inline", _style="margin: 5px 0px")
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

        buttons = DIV(DIV(_btn_back, *btns, _class='row_buttons'), _class="web2py_grid")
        table = DIV(DIV(info), DIV(B('Member: '), member.first_name+' '+member.last_name, _class='p-2', _style='background: #eaeaea'), t)

        form = reason_form

        has_errors = 'False'
        if form:
            if form.process().accepted:
                session.disapprove_sr_reason = form.vars['reason']
                redirect(URL('record_change_sr_request', args=['disapprove', request.args(1), request.args(2) ], user_signature=True))
            elif form.errors:
                has_errors = 'True'
                response.flash = '' # no need for flash messages, error hint is enough

        return dict(table=table, form=form, buttons=buttons, has_errors=has_errors)

    elif request.args(0)=='approve':
        r = db.service_record(request.args(2)) or HTTP(400)
        r.update_record(status='approved', reason='')

    elif request.args(0)=='disapprove':
        r = db.service_record(request.args(2)) or HTTP(400)
        r.update_record(status='disapproved', reason=session.disapprove_sr_reason)
        del session.disapprove_sr_reason

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
