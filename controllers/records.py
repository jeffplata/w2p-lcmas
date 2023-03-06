# -*- coding: utf-8 -*-
# try something like
@auth.requires_login()
def index(): 
    return dict(message="hello from records.py")

@auth.requires_login()
def record_dash():
    link1 = dict(header='', body=lambda r: A('View', _class='button btn btn-default btn-secondary', 
        _href=URL('default','record_dash', args=['view', 'member_info_update_request', r.id], user_signature=True), cid=request.cid ))
    d = None
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

    grid = SQLFORM.grid(db.member_info_update_request, orderby=~db.member_info_update_request.id,
        create=False, formname='grid_mem', deletable=False, csv=False, links=[link1])
    return dict(grid=grid, form=d)
