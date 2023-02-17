
me = auth.user_id

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

db.define_table("user_info",
    Field("user_id", "reference auth_user"),
    Field("employee_no", length=20)
    )