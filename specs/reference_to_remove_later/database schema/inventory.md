



===============================
INVENTORY MODULE:
===============================

inventory_types:
   id
   name - type of inventory (e.g., TV , battery 9000mAh, raw materials, spare parts, consumable, office supply, finished goods, Food Supplies, Fuel Supplies)
   description
   status - active, inactive
   created_at
   updated_at

inventory_groups:
   id
   name - name of the group (e.g., raw materials, finished goods, consumables)
   inventory_type_id - foreign key to inventory_types table
   description
   status - active, inactive
   created_at
   updated_at

item_categories:
   id
   inventory_type_id - foreign key to inventory_types table
   name - name of the category (e.g., TV 32 inch, TV 40 inch, TV 50 inch, battery 9000mAh, battery 10000mAh, battery 11000mAh , direct raw materials, indirect raw materials)
   description
   status - active, inactive
   created_at
   updated_at

inventory_locations:
   id
   name - name of the location (e.g., warehouse, store, office)
   branch_id - foreign key to branches table
   code - code of the location
   description
   status - active, inactive
   created_at
   updated_at

inventory_items:
   id                             serial primary key,
   sku                            varchar(100) unique,
   name                           varchar(255) not null,
   image                          varchar(255), 
  
   quantity                       numeric(18,2) default 0,
   reserved_quantity              numeric(18,2) default 0,
   reorder_level                  numeric(10,2),
   purchase_opening_date          date,
   expiry_date                    date,


   cost_currency_id               integer references currencies(id),
   cost_unit_exchange             
   unit_cost                      numeric(18,2) not null default 0,
   other_cost_per_unit            numeric(18,2) default 0,
   total_cost                     numeric(18,2) default 0,


   sales_currency_id              integer references currencies(id),
   sales_unit_price               numeric(18,2),


   reference_no                   varchar(100),
   company_id                     integer references company(id),
   cost_center_id                 integer references cost_center(id),
   usage_unit_id                  integer references units(id),
   is_merchandise                 boolean default false,
   purchase_date                  date,


   model                          varchar(100),
   made_in                        varchar(100),
   made_by                        varchar(100),
   status                         varchar(50), -- e.g., new, damaged, expired, etc.
   description                    text,
   note                           text,
   custom_fields                  jsonb, -- for custom dynamic fields
 
   quality_id                     integer references inventory_quality(id),
   branch_id                      integer references branches(id),
   warehouse_location_id          integer references inventory_locations(id),
   inventory_type_id              integer references inventory_types(id),
   item_category_id               integer references item_categories(id),
   inventory_group_id             integer references inventory_groups(id),
   purchase_unit_id               integer references units(id),


   created_by_id                  integer references users(id),
   updated_by_id                  integer references users(id),
   created_at                     timestamptz default now(),
   updated_at                     timestamptz default now()

inventory_items_components:
   id
   inventory_item_id - foreign key to inventory_items table
   name - name of the component
   quantity - quantity of the component
   unit_price - unit price of the component
   total_price - total price of the component
   created_at
   updated_at


inventory_media:
   id                          serial primary key,
   inventory_item_id           integer references inventory_items(id) not null,
   file_path                   varchar(255) not null, -- file path or URL to the image
   title                       varchar(255),
   description                 text,
   uploaded_at                 timestamptz default now()

inventory_quality:
   id
   name
   description
   created_at
   updated_at

inventory_item_price: 
   id
   inventory_item_id - foreign key to inventory_items table
   retail_price - retail price of the inventory item
   wholesale_price - wholesale price of the inventory item
   currency_id - foreign key to currencies table
   exchange_rate - exchange rate of the currency
   branch_id - foreign key to branches table
   created_at
   updated_at

# stock dispose
# stock ajustment
# production request
# inidvitual request
# repaire_maintainance request
# delivery order request
# internal transfer
# sales return

inventory_request:
   id
   stock_request_number - varchar(100) - SRN24-0001
   cost_center_id - foreign key to cost_centers table
   requested_by_id - foreign key to users table
   approved_by_id - foreign key to users table (nullable)
   branch_id - foreign key to branches table
   request_for - foreign key to users table  - this is used for individual request (morphed table)
   transferred_from - foreign key to branches table
   transferred_to - foreign key to branches table
   transferred_by - foreign key to users table
   transferred_at - timestamp
   transferred_status - enum: pending, approved, rejected, completed, cancelled
   transferred_note - text
   disposed_type - enum: sold, donate, burn, recycle, trash, other, lost, damaged, expired
   disposed_by - foreign key to users table 
   disposed_at - timestamp 
   disposed_note - text 
   disposed_attachments - varchar(255) 
   disposed_status - enum: pending, approved, rejected, completed, cancelled
   adjustment_type - enum: add, subtract
   adjustment_by - foreign key to users table
   adjustment_at - timestamp
   adjustment_note - text
   adjustment_attachments - varchar(255)
   adjusted_status - enum: pending, approved, rejected, completed, cancelled
   repair_maintenance_note - varchar(100)
   return_reason - text
   return_attachments - varchar(255)
   request_type - enum: dispose, adjustment, production, individual, repair_maintenance, transfer, sales_return
   total_quantity
   status - pending, approved, rejected, completed, cancelled
   reference_no
   description
   note
   request_date
   processed_date
   created_at
   updated_at

   
inventory_request_items:
   id
   inventory_request_id - foreign key to inventory_request table
   inventory_item_id - foreign key to inventory_items table
   quantity - quantity of the inventory item
   unit_price - unit price of the inventory item
   created_at
   updated_at


inventory_transactions:
   id
   transaction_number - transaction number (e.g., TRN24-0001)
   type - enum: production, purchase order, normal/other 
   quantity - quantity of the inventory item
   unit_cost - unit price of the inventory item
   other_cost - other cost of the inventory item
   exchange_rate - exchange rate of the currency
   
   currency_id - foreign key to currencies table
   warehouse_location_id - foreign key to inventory_locations table
   inventory_item_id - foreign key to inventory_items table
   purchase_order_id - foreign key to purchase_orders table - nullable 
   production_job_id - foreign key to production_jobs table - nullable 
   branch_id - foreign key to branches table

   created_at
   updated_at





-------------------------------------
INVENTORY MODULE FLOWS: 
-------------------------------------

-- inventory_entry flow:
      0. ::::::::::::::: start-flow :::::::::::::::
      1. this will be handled when the items are comming from procurement module. 
    6. ::::::::::::::: end-flow :::::::::::::::

-- inventory recept flow: 
      0. ::::::::::::::: start-flow :::::::::::::::
      1. this will be handled when the items are comming from procurement module. 
    6. ::::::::::::::: end-flow :::::::::::::::

-- stock dispose request
    0. ::::::::::::::: start-flow :::::::::::::::
    1. user create a stock dispose request
    2. inventory manager specify the inventory item for stock dispose via inventory request items
    3. the inventory request will be directly visible to approving authority for approval
    4. the approving authority will check if rejected then the request will be visible for edit to stock dispose manager else move to next step
    5. after the disposing approval the selected item quantity will be deducted from inventory (inventory will take effect) and added to disposed items. 
    6. ::::::::::::::: end-flow :::::::::::::::

stock ajustment request
    0. ::::::::::::::: start-flow :::::::::::::::
    1. user create a stock ajustment request
    2. inventory manager specify the inventory item for stock ajustment via inventory request items
    3. the inventory request will be directly visible to approving authority for approval
    4. the approving authority will check if rejected then the request will be visible for edit to stock ajustment manager else move to next step
    5. after the ajustment approval the selected item quantity will be deducted /added from inventory (inventory will take effect) and added to ajustment items. 
    6. ::::::::::::::: end-flow :::::::::::::::

-- production request flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. user create a production request
    2. user specify the direct and indirect raw material for production job via inventory request items
    3. the inventory request will be directly visible to stock/inventory manager or user 
    4. the inventory manager will check if rejected then the request will be visible for edit to production manager else move to next step
    5. stock manager will prepared requested materials(direct & indirect raw material) - stockout operation 
    6. move/sent/transfer  the material to production 
    7. upon physical checkup if production manager reject the recieved item , the stock will be able to modify the rejected item and re-stockout it
    8. production manager will be receieve the item and then after production manager the stockout quantity will take effect in inventory 
    9. ::::::::::::::: end-flow :::::::::::::::

-- inidvitual request flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. user create a inidvitual request with desired items  - system will tell if the item is not available then no request can be made instead it will be a purchase request
    2. the inventory request will be directly visible to stock/inventory manager and approving authority for approval in approval system 
    3. once the request is approved by approving authority then the inventory manager will issue the requested item to the user and inventory will take effect
    4. ::::::::::::::: end-flow :::::::::::::::
    
-- delivery order request flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create a delivery order request
    2. the delivery order request will be directly visible to stock/inventory manager if rejected then the request will be visible for edit to sales manager else move to next step
    3. once the request is approved by the inventory manager then the inventory manager will issue the requested item to the customer and inventory will take effect
    4. ::::::::::::::: end-flow :::::::::::::::
    
-- internal transfer request flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. inventory manager create a internal transfer request
    2. the internal transfer request will be directly visible to approving authority if rejected then the request will be visible to rejected request list  else move to next step
    3. once the request is approved by the approving authority then the inventory manager will issue the physical transfer from one branch to another branch
    4. ::::::::::::::: end-flow :::::::::::::::

-- sales return request flow:
    0. ::::::::::::::: start-flow :::::::::::::::
    1. sales team create a sales return request
    2. the sales return request will be directly visible to stock/inventory manager and approving authority for approval in approval system if rejected then the request will be visible in rejected list  else move to next step
    3. once the request is approved by the inventory manager then the inventory manager will return or restock  the requested item from the customer and inventory will take effect (stockk will increase)
    4. ::::::::::::::: end-flow :::::::::::::::













