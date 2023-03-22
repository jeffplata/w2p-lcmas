
def record_pages():
    return dict(page=request.args(0))

def dashboard():
    pending_requests = db(db.member_info_update_request.status=='pending').count()
    total_requests = db(db.member_info_update_request).count()
    pending_sr_requests = db(db.service_record.status=='pending').count()
    total_sr_requests = db(db.service_record.status).count()
    total_members = len(db(db.auth_membership.group_id==auth.id_group('member')).select(groupby=(db.auth_membership.user_id,db.auth_membership.group_id)))
    total_non_members = db(db.auth_user).count() - total_members

    # todo: retrieve all defined groups for at-a-glance view, try sub-select
    count = db.auth_membership.id.count()
    groups = db().select(db.auth_membership.group_id, db.auth_group.role, count, 
        left=db.auth_group.on(db.auth_membership.group_id==db.auth_group.id),
        groupby=db.auth_membership.group_id)
    print(db._lastsql)
    group_links = []
    for g in groups:
        url = URL('records', 'record_users', args=['list_group', g.auth_membership.group_id, g.auth_group.role], user_signature=True)
        group_links += [A(B('%s (%s)' % (g.auth_group.role, g[count])), _href=url, cid='record_users_div'), SPAN(' | ')]
    group_links = group_links[:-1]
    group_links = DIV(group_links, _class="text-center")
    return locals()