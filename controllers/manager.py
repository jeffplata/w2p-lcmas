
def record_pages():
    return dict(page=request.args(0))

def dashboard():
    pending_requests = db(db.member_info_update_request.status=='pending').count()
    total_requests = db(db.member_info_update_request).count()
    pending_sr_requests = db(db.service_record.status=='pending').count()
    total_sr_requests = db(db.service_record.status).count()
    total_members = len(db(db.auth_membership.group_id==auth.id_group('member')).select(groupby=(db.auth_membership.user_id,db.auth_membership.group_id)))
    total_non_members = db(db.auth_user).count() - total_members

    count = db.auth_membership.id.count()
    groups = db().select(db.auth_membership.group_id, db.auth_group.role, count, groupby=db.auth_membership.group_id,
        join=db.auth_group.on(db.auth_group.id==db.auth_membership.group_id))
    s = ''
    for g in groups:
        s = s + '%s - %s |' % (g.auth_group.role, g[count])
    return locals()