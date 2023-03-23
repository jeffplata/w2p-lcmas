

@auth.requires_login()
def member_dash():
    import datetime
    services = db(db.service).select()
    loans = {'date':'01/16/2023', 'type':'MCLP', 'amount':52000, 'balance':52000, 'status':'submitted'}
    tav = 100290.00
    last_cont_date = datetime.datetime(2023,1,9)
    last_cont_amt = 2045.00
    return locals()


def loan_success():
    return locals()


def check_agree(form):
    if not form.vars.agree:
        form.errors.agree = 'You must agree to the Statement of undertaking'

@auth.requires_login()
def apply_for_loan():

    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('member_dash'), 
        cid=request.cid, _class='btn btn-secondary')

    service_id = request.args(0)
    service = db(db.service.id==service_id).select().first()
    db.loan.service_id.default = service_id
    db.loan.member_id.default = auth.user_id

    form = SQLFORM(db.loan, fields=["principal_amount", "terms",], formname='loan_form')
    if form.process(onvalidation=check_agree, dbio=False).accepted:
        redirect(URL('loan_success'))

    d = DIV(INPUT(_type="checkbox", _id="agree", value=False)," I agree to the statement of undertaking", BR(), BR(), _class="p-1")
    form[0].insert(2, d)
    form.element('#submit_record__row')[1].insert(1, _btn_back)
    return locals()