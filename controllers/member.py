

@auth.requires_login()
def member_dash():
    import datetime
    services = db(db.service).select()
    loans = {'date':'01/16/2023', 'type':'MCLP', 'amount':52000, 'balance':52000, 'status':'submitted'}
    tav = 100290.00
    last_cont_date = datetime.datetime(2023,1,9)
    last_cont_amt = 2045.00
    session.flash = ''
    return locals()


def loan_success():
    return locals()


def check_loan(form):
    if not form.vars.agree:
        form.errors.agree = ''
    if float(form.vars.principal_amount) <= 0:
        form.errors.principal_amount = 'Enter an amount greater than zero (0).'
    if not form.errors:
        db.loan.loan_number.default = '2023-001'


@auth.requires_login()
def apply_for_loan():

    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('member_dash'), 
        cid=request.cid, _class='btn btn-secondary')

    service_id = request.args(0)
    service = db(db.service.id==service_id).select().first()
    db.loan.service_id.default = service_id
    db.loan.member_id.default = auth.user_id

    # form = SQLFORM(db.loan, fields=["principal_amount", "terms"], formname='loan_form')
    form = SQLFORM(db.loan, fields=['principal_amount', 'terms'], formname='loan_form')

    lorem = '''
        In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content. Lorem ipsum may be used as a placeholder before final copy is available.
    '''

    d = TABLE(
            TR(
                TD(
                    INPUT(_type="checkbox", _id="loan_agree", _name='agree', value=False),
                    _style='width:25px; vertical-align: top;'
                ),
                TD(
                    DIV("I agree to the statement of undertaking " +lorem, _class='text-justify'),
                    DIV('You must agree to the statement of undertaking.', _class='error ', _style='padding:5px 0 5px 0', _id='must_agree')
                )
            )
        , _style='margin-bottom: 15px;')

    form[0].insert(2, d)
    form.element('#submit_record__row')[1].insert(1, _btn_back)

    if form.process(onvalidation=check_loan).accepted:
        response.flash  = ''
        redirect(URL('loan_success'))
    elif form.errors:
        response.flash = ''
        if form.vars.agree != 'on':
            response.js = "jQuery('#must_agree').show();"
        else:
            response.js = "jQuery('#must_agree').hide();"
    else:
        response.js = "jQuery('#must_agree').hide();"

    return locals()