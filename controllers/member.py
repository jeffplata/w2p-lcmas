from datetime import datetime
import re

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


def get_next_number(table, next_number, number_format):
    fld = db[table][next_number]
    db.executesql('update %s set %s=%s+1;' % (table, next_number, next_number))
    r = db.executesql('select %s, %s from %s' % (next_number, number_format, table))
    nxn = r[0][0]
    fmt = r[0][1]
    fmt = datetime.now().strftime(fmt)
    nph = re.search('\[0+\]', fmt)
    nph = re.sub('[\[\]]', '', nph[0])
    if len(nxn) >= len(nph):
        nph = nxn
    else:
        nph = nph[0:len(nph)-len(nxn)] + nxn
    nxn = re.sub('\[0+\]', nph, fmt)
    return nxn


def check_loan(form):
    if not form.vars.agree:
        form.errors.agree = ''
    if float(form.vars.principal_amount) <= 0:
        form.errors.principal_amount = 'Enter an amount greater than zero (0).'
    if not form.errors:
        db.loan.loan_number.default = get_next_number('loan_number', 'next_number', 'number_format')


def compute_net_proceeds():
    amount = float(request.vars.principal_amount)
    fee = float(session.selected_service.service_fee)
    bal = 5500.00
    fee = fee * .01 * amount
    net = amount - fee
    bal = moneytize(bal)
    fee = moneytize(fee)
    net = moneytize(net)
    s = H4('Computations')
    s = DIV(s, TABLE(
            COLGROUP(COL(_width="25%"), COL(_width="15%")),
            TR( TD('Previous balance:'), bal, _align="right"),
            TR( TD('Processing fee:'), fee, _align="right" ),
            TR( TD('NET PROCEEDS:'), net, _align="right" ),
        ))
    return s


def compute_amortization():
    terms = int(request.vars.terms)
    amount = float(request.vars.principal_amount)
    start_date = datetime.now().date()
    start_date = start_date.replace(day=30)
    force_day = start_date.day
    ideal_bal = amount
    int_rate = float(session.selected_service.interest_rate) * .01
    mo_prin = round(amount/terms,2)
    mo_int = round(ideal_bal * int_rate, 2)

    s = H4('Amortization')
    tb  = TABLE(_class='table')
    t = [[0]*5 for i in range(terms)]
    for i in t:
        start_date = next_month(start_date, force_day)
        i[0] = start_date.strftime('%m/%d/%Y')
        i[1] = mo_prin if mo_prin < ideal_bal else ideal_bal
        i[2] = mo_int
        i[3] = mo_prin + mo_int
        i[4] = round(ideal_bal - mo_prin, 2) if mo_prin < ideal_bal else 0
        ideal_bal = i[4]
        tb.append(TR(i[0], i[1], i[2], i[3], i[4]))
    s = DIV(s, t)
    return s


@auth.requires_login()
def apply_for_loan():

    _btn_back = A(SPAN(_class="icon arrowleft icon-arrow-left glyphicon glyphicon-arrow-left"),
        ' Back', _href=URL('member_dash'), 
        cid=request.cid, _class='btn btn-secondary')

    service_id = request.args(0)
    service = db(db.service.id==service_id).select().first()
    session.selected_service = service
    db.loan.service_id.default = service_id
    db.loan.member_id.default = auth.user_id

    form = SQLFORM(db.loan, fields=['principal_amount', 'terms'], formname='loan_form')

    lorem = '''
        In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the 
        visual form of a document or a typeface without relying on meaningful content. Lorem ipsum may be used 
        as a placeholder before final copy is available.
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