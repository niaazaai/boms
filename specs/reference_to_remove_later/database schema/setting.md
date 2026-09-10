


===============================
setting
===============================


payment_methods
   id
   name
   created_at
   updated_at


payment_terms
   id
   name
   created_at
   updated_at


branches
   id
   name
   location
   staff_count
   branch_manager
   created_at
   updated_at


company
   id
   name
   license_number
   license_expiry_date
   license_attachments
   created_at
   updated_at


cost_center
   id
   name
   description
   created_at
   updated_at


need_assessment_periods:
   id
   title - default monthly, quarterly, annually
   description - description of the need assessment period
   created_at
   updated_at


currencies:
   id
   name
   code
   symbol
   created_at
   updated_at


incoterms:
   id
   code - incoterm code
   description - incoterm description
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


freight_types:
   id
   name - Land , Sea , Air , land and sea
   description - freight type description
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


ports:
   id
   port_name - port name ( )
   country_id - foreign key to countries table
   description - port description
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


charge_types:
   id
   name - e.g., "Miscellaneous Exp.", "Detention Charges", "Storage Fees", "Bank/Sarafi Charges", "Tariff", "Inland Transportation Costs", "Freight Charges"
   description - brief explanation of the charge type
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


purchase_account_types:
   id
   code - e.g., 500, 400, 300, 200, 100
   name - e.g., "Repairs & Maintenance", "Fuel", "Food Supplies", "Stationery", "Official Travel"
   account_group - e.g., "Ind. Purchase Request", "Miscellaneous Expenses"
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


discounts:
   id
   name - name of the discount (e.g., seasonal, promotional)
   description - description of the discount
   discount_type - percentage, fixed_amount
   value - discount value (e.g., 10 for 10% or 100 for fixed 100 units)
   start_date - discount valid from
   end_date - discount valid until
   status - active, inactive
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at


units: (measurement units)
   id
   name         - name of the usage unit (e.g., kilogram, liter, piece)
   short_code   - short code or symbol for unit (e.g., kg, L, pcs)
   description  - description of the unit
   status       - active, inactive
   created_at
   updated_at






user_logs
users


================
optional tables:
================


established_thresholds
   id
   min_value - minimum value of the established threshold
   max_value - maximum value of the established threshold
   branch_id - foreign key to branches table
   currency_id - foreign key to currencies table
   threshold_type - global, local, internal
   approving_authority - array of user ids
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

