
from datetime import datetime
me = auth.user_id
mdy = '%m/%d/%Y'
mdy_date = IS_DATE(format='%m/%d/%Y')

db.define_table("service_payment_type",
    Field("name", "string", requires=[IS_NOT_EMPTY(), IS_SLUG()]),
    format = '%(name)s')

db.define_table("service",
    Field("name","string", requires=[IS_NOT_EMPTY()]),
    Field("description","string"),
    Field("interest_rate","decimal(6,2)",default=0),
    Field("surcharge_rate","decimal(6,2)",default=0),
    Field("service_fee","decimal(6,2)",default=0),
    Field("minimum_amount", "decimal(15,2)", default=0, 
        represent=lambda v, r: '{:,}'.format(v) if v is not None else ''),
    Field("maximum_amount", "decimal(15,2)", default=0, 
        represent=lambda v, r: '{:,}'.format(v) if v is not None else ''),
    Field("payment_type_id", "reference service_payment_type", label="Payment Type"),
    )

db.service.payment_type_id.requires = IS_IN_DB(db, db.service_payment_type.id, '%(name)s', zero=None)

db.auth_user.format = "%(last_name)s"

db.define_table("loan",
    Field("loan_number", "string", requires=IS_NOT_EMPTY()),
    Field("member_id", "reference auth_user"),
    Field("service_id", "reference service"),
    Field("principal_amount", "decimal(15,2)", default=0, ),
    Field("interest_rate", "decimal(6,2)", default=0),
    Field("interest_amount", "decimal(15,2)", default=0),
    Field("surcharge_rate", "decimal(6,2)", default=0),
    Field("surcharge_amount", "decimal(15,2)", default=0),
    Field("service_fee_rate", "decimal(6,2)", default=0),
    Field("service_fee_amount", "decimal(15,2)", default=0),
    Field("terms", "integer", default=12),
    Field("deductions_amount", "decimal(15,2)", default=0),
    Field("net_proceeds", "decimal(15,2)", default=0),


    auth.signature
    )

db.define_table('department',
    Field('name', length=80, requires=IS_NOT_EMPTY()),
    Field('short_name', length=20, requires=IS_NOT_EMPTY()),
    format='%(name)s'
    )

db.define_table("member_info",
    Field("user_id", "reference auth_user"),
    Field("employee_no", length=20, requires=IS_NOT_EMPTY()),
    Field("birth_date","date", requires=[IS_DATE(format='%m/%d/%Y'),IS_NOT_EMPTY()]),
    Field("gender", length=6, requires=IS_IN_SET(["male", "female", ])),
    Field("civil_status", length=10, requires=IS_IN_SET(["single", "married", "divorced", "separated", "widowed", ])),
    Field("mobile_number", length=80),
    Field("home_address", length=128),
    Field("date_membership", "date", requires=IS_DATE(format='%m/%d/%Y')),
    Field("entrance_to_duty", "date", requires=IS_DATE(format='%m/%d/%Y')),
    auth.signature,
    )

db.define_table('service_record',
    Field('user_id', 'reference auth_user', label='Member'),
    Field('date_effective', 'date', requires=mdy_date),
    Field('department_id', 'reference department', label='Department'),
    Field('mem_position', length=50, label='Position'),
    Field('salary', 'decimal(15,2)', represent=lambda v, r: '{:,}'.format(v) if v is not None else ''),
    Field('status', length=11, default='pending', requires=IS_IN_SET(['pending', 'approved', 'disapproved', 'system']),
        represent = lambda v, r : DIV('pending', _class='bg-warning') if v=='pending' else v),
    Field('reason', length=128, readable=False),
    auth.signature,
    )

db.define_table('service_record_attachment',
    Field('service_record_id', 'reference service_record'),
    Field('doc', 'upload'),
    )

db.define_table("member_info_update_request",
    Field("user_id", "reference auth_user", label='Member'),
    Field("first_name", length=80, requires=IS_NOT_EMPTY()),
    Field("last_name", length=80, requires=IS_NOT_EMPTY()),
    Field("middle_name", length=80),
    Field("employee_no", length=20),
    Field("birth_date", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("gender", length=6),
    Field("civil_status", length=10),
    Field("date_membership", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("entrance_to_duty", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("date_submitted", "date", default=datetime.today, requires=mdy_date),
    Field('status', length=11, default='pending', requires=IS_IN_SET(['pending', 'approved','disapproved']), 
        represent = lambda v, r : DIV('pending', _class='bg-warning') if v=='pending' else v),
    Field('reason', length=128, readable=False),
    auth.signature,
    )

db.define_table("member_info_update_request_hist",
    Field('request', 'reference member_info_update_request'),
    Field("user_id", "reference auth_user", label='Member'),
    Field("first_name", length=80, requires=IS_NOT_EMPTY()),
    Field("last_name", length=80, requires=IS_NOT_EMPTY()),
    Field("middle_name", length=80),
    Field("employee_no", length=20),
    Field("birth_date", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("gender", length=6),
    Field("civil_status", length=10),
    Field("date_membership", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("entrance_to_duty", "date", requires=IS_EMPTY_OR(mdy_date)),
    Field("date_submitted", "date", requires=mdy_date),

    )