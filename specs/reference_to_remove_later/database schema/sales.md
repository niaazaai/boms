===============================
SALES MODULE:
===============================

scm_customers:
   id
   customer_name - varchar(256) unique
   customer_code - varchar(128)
   contact_person - varchar(128)
   job_title - varchar(128)
   gender - enum: male, female
   reference - varchar nullable
   quotation_sending_address - varchar(256) nullable
   shipment_address - varchar(256) nullable
   time_line - unsigned integer
   full_address - varchar(256)
   location_link - varchar(256) nullable
   note - text nullable
   custom_fields - json nullable
   status - enum: prospect, active, inactive, etc.
   approval_status - enum: pending, approved, rejected
   module - enum: sales, etc.
   finance_recorded - boolean default false
   last_order_date - datetime nullable
   is_agent - boolean default false
   category_id - foreign key to categories table
   specification_id - foreign key to specifications table
   business_type_id - foreign key to business_types table
   branch_id - foreign key to branches table
   payment_term_id - foreign key to payment_terms table
   country_id - foreign key to countries table
   state_id - foreign key to states table
   region_id - foreign key to regions table
   sub_cost_center_id - foreign key to sub_cost_centers table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at

scm_customer_accounts:
   id
   customer_id - foreign key to scm_customers table
   currency_id - foreign key to currencies table
   opening_balance - integer default 0
   credit_limit - integer default 0
   credit_balance - integer default 0
   debit_balance - integer default 0
   total_balance - integer default 0
   opening_balance_type - enum: credit, debit
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at

scm_customer_approvals:
   id
   customer_id - foreign key to scm_customers table
   type - enum: new_registration, etc.
   comment - text nullable
   status - enum: pending, approved, rejected
   completed_at - datetime nullable
   action_by_id - foreign key to users table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_customer_gifts:
   id
   customer_id - foreign key to scm_customers table
   inventory_sales_gift_id - foreign key to scm_inventory_sales_gifts table
   target - decimal(20,3) unsigned
   status - enum: pending, active, completed, etc.
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   action_by_id - foreign key to users table
   created_at
   updated_at

scm_customer_seasons:
   id
   customer_id - foreign key to scm_customers table
   season_id - foreign key to bgpkg_seasons table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_orders:
   id
   order_no - varchar(128) nullable
   sales_type - enum: daily_sales, etc.
   type - enum: quotation, order, invoice
   location - enum: quotation, order, invoice
   deadline - date
   po_number - varchar(128) nullable
   note - text nullable
   status - enum: new, prospect, postponed, under_evaluation, follow_up_required, finance_new, underloading, delivered, issued, cancelled, etc.
   previous_status - enum: same as status
   status_note - text nullable
   currency_id - foreign key to currencies table
   exchange_rate - decimal(20,4)
   discount - decimal(20,4)
   bonus - decimal(20,4)
   tax - decimal(20,4)
   other_charges - decimal(20,4)
   sub_total - decimal(20,4)
   total - decimal(20,4)
   grand_total - decimal(20,4)
   base_sub_total - decimal(20,4)
   base_grand_total - decimal(20,4)
   base_total - decimal(20,4)
   total_cost - decimal(20,4)
   total_returned - decimal(20,4) default 0
   processed_avg - float default 0
   order_date - datetime nullable
   invoice_date - datetime nullable
   quotation_date - datetime nullable
   cancelled_at - datetime nullable
   finance_approved_at - datetime nullable
   approval_status - enum: pending, approved, rejected
   quotation_id - foreign key to scm_quotations table nullable
   order_by_id - foreign key to users table nullable
   verified_by_id - foreign key to users table nullable
   customer_id - foreign key to scm_customers table
   payment_method_id - foreign key to payment_methods table
   payment_term_id - foreign key to payment_terms table
   branch_id - foreign key to branches table
   sub_cost_center_id - foreign key to sub_cost_centers table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at

scm_order_items:
   id
   order_id - foreign key to scm_orders table
   inventory_item_id - foreign key to scm_inventory_items table nullable
   justification - text nullable (for non-inventory items)
   reference_no - varchar(128)
   quantity - decimal(20,3) unsigned
   return_quantity - decimal(20,3) default 0
   bonus_quantity - decimal(20,3) unsigned
   unit_price - decimal(20,4) unsigned
   original_unit_price - decimal(20,4) unsigned
   last_unit_price - decimal(20,4) unsigned
   total_bonus - decimal(20,4) unsigned
   total_price - decimal(20,2) unsigned
   base_unit_price - decimal(20,4) unsigned
   base_total_bonus - decimal(20,4) unsigned
   base_total_price - decimal(20,2) unsigned
   unit_cost - decimal(20,4) unsigned
   exchange_rate - decimal(20,4)
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_items_details:
   id
   order_item_id - foreign key to scm_order_items table
   commission_amount - decimal(20,4) unsigned
   commission_to_id - foreign key to users table nullable
   created_at
   updated_at

scm_quotations:
   id
   quotation_no - varchar(128)
   status - enum: prospect, postponed, follow_up_required, under_evaluation, etc.
   previous_status - enum: same as status
   status_note - text nullable
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_invoices:
   id
   order_id - foreign key to scm_orders table
   invoice_no - varchar(128)
   status - enum: finance_new, postponed, underloading, delivered, issued, etc.
   previous_status - enum: same as status
   status_note - text nullable
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_returns:
   id
   reference_no - varchar(128)
   order_id - foreign key to scm_orders table
   exchange_rate - decimal(20,4) unsigned
   other_charges - decimal(20,4) unsigned
   note - text nullable
   status - enum: pending, approved, rejected
   approved_at - datetime nullable
   currency_id - foreign key to currencies table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_return_items:
   id
   order_return_id - foreign key to scm_order_returns table
   order_item_id - foreign key to scm_order_items table
   quantity - decimal(20,3) unsigned
   bonus_quantity - decimal(20,3) unsigned
   unit_price - decimal(20,4) unsigned
   base_unit_price - decimal(20,4) unsigned
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_adjustments:
   id
   reference_no - varchar(128) unique
   order_id - foreign key to scm_orders table
   exchange_rate - decimal(20,4) unsigned
   type - enum: add, subtract
   note - text nullable
   status - enum: pending, approved, rejected
   approved_at - datetime nullable
   currency_id - foreign key to currencies table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_adjustment_items:
   id
   order_adjustment_id - foreign key to scm_order_adjustments table
   order_item_id - foreign key to scm_order_items table
   quantity - decimal(20,3) unsigned
   old_unit_price - decimal(20,4) unsigned
   unit_price - decimal(20,4) unsigned
   base_unit_price - decimal(20,4) unsigned
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_order_approvals:
   id
   order_id - foreign key to scm_orders table
   type - enum: finance, manager, etc.
   status - enum: pending, approved, rejected
   meta - json nullable
   completed_at - datetime nullable
   comment - text
   action_by_id - foreign key to users table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_follow_ups:
   id
   followable_type - polymorphic type
   followable_id - polymorphic id
   next_follow_up_date - datetime
   comment - varchar(1082) nullable
   status - enum: active, closed, etc.
   contact_via - enum: email, phone, whatsapp, etc.
   closed_reason - enum: completed, cancelled, etc. nullable
   type - enum: quotation, customer, etc.
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_sales_events:
   id
   eventable_type - polymorphic type
   eventable_id - polymorphic id
   location - enum: quotation, order, invoice, customer, etc.
   action - enum: created, updated, cancelled, approved, rejected, etc.
   approval_visible - boolean default true
   comment - text nullable
   importance_level - enum: low, medium, high, etc. nullable
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_sales_summaries:
   id
   customer_id - foreign key to scm_customers table nullable
   inventory_item_id - foreign key to scm_inventory_items table nullable
   first_order_date - datetime nullable
   last_order_date - datetime nullable
   quantity - decimal(20,3) default 0
   bonus_quantity - decimal(20,3) default 0
   no_of_orders - decimal(20,3) default 0
   monthly - decimal(20,3) default 0
   total_amount - decimal(20,3) default 0
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at

scm_sales_commissions:
   id
   commission - decimal(12,4)
   inventory_item_id - foreign key to scm_inventory_items table
   branch_id - foreign key to branches table
   currency_id - foreign key to currencies table
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at
   unique constraint: (inventory_item_id, branch_id, currency_id)

scm_sales_bonuses:
   id
   branch_id - foreign key to branches table
   sales_target - integer
   current_amount - integer
   currency_id - foreign key to currencies table
   start_date - date
   end_date - date
   bonus - integer
   status - enum: running, completed, cancelled, etc.
   action_status - enum: same as status nullable
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at

scm_sales_gifts:
   id
   name - varchar(180)
   description - varchar
   created_by_id - foreign key to users table
   updated_by_id - foreign key to users table
   created_at
   updated_at
   deleted_at

scm_contacts: (shared table - polymorphic)
   id
   contactable_type - polymorphic type
   contactable_id - polymorphic id
   personal_phone_number - varchar nullable
   work_phone_number - varchar nullable
   whatsapp_number - varchar nullable
   main_email - varchar nullable
   cc_email - varchar nullable
   website - varchar nullable
   social_media - json nullable
   created_at
   updated_at

scm_media: (shared table - polymorphic)
   id
   mediable_type - polymorphic type
   mediable_id - polymorphic id
   file_path - varchar(255)
   title - varchar(255) nullable
   description - text nullable
   uploaded_at - timestamptz default now()
   created_at
   updated_at

-------------------------------------
SALES MODULE FLOWS: 
-------------------------------------

-- quotation flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create a quotation request with customer and items
    2. quotation will be visible to sales manager for review
    3. quotation can be sent to customer
    4. quotation status can be: prospect, postponed, follow_up_required, under_evaluation
    5. quotation can be converted to order
    6. ::::::::::::::: end-flow :::::::::::::::

-- order flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create an order (can be from quotation or directly)
    2. order will be visible to inventory manager for stock check
    3. order can be approved/rejected by inventory manager
    4. approved order can be converted to invoice
    5. ::::::::::::::: end-flow :::::::::::::::

-- invoice flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. order is converted to invoice
    2. invoice status: finance_new, postponed, underloading, delivered, issued
    3. finance approval required for invoice processing
    4. inventory manager prepares items for delivery (underloading)
    5. items are delivered to customer (delivered)
    6. invoice is issued (issued)
    7. ::::::::::::::: end-flow :::::::::::::::

-- order return flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create a return request for an order/invoice
    2. return request includes items and quantities to return
    3. return request requires approval
    4. once approved, inventory is restocked and customer account is adjusted
    5. ::::::::::::::: end-flow :::::::::::::::

-- order adjustment flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create an adjustment request for an order/invoice
    2. adjustment can be add or subtract type
    3. adjustment request includes items and price changes
    4. adjustment request requires approval
    5. once approved, order totals are adjusted
    6. ::::::::::::::: end-flow :::::::::::::::

-- customer management flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create a customer record
    2. customer requires approval (new_registration)
    3. customer can be: prospect, active, inactive
    4. customer account can be set up with credit limits
    5. customer can have seasons assigned
    6. customer can receive gifts based on sales targets
    7. ::::::::::::::: end-flow :::::::::::::::

-- follow-up flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. follow-ups can be created for quotations or customers
    2. follow-up has next_follow_up_date and contact_via
    3. follow-up status: active, closed
    4. closed follow-ups have closed_reason
    5. ::::::::::::::: end-flow :::::::::::::::

-- sales summary flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales summaries are generated/updated based on orders
    2. tracks customer sales by inventory item
    3. includes: first_order_date, last_order_date, quantity, bonus_quantity, no_of_orders, monthly, total_amount
    4. ::::::::::::::: end-flow :::::::::::::::

