 


users
    id (PK)
    name 
    email 
    ... 


tenant
    id (PK)
    code   - i.e. ADF 
    name
    phone_number 
    address 
    website_url 





common columns in all tables bellow: created_at , update_at , updated_by , created_by , tenant_id 
PLATFORM MODULE : 

    branches
        id (PK)
        code
        name
    
    units 
        id 
        code 
        name 
    
    currencies 
        id 
        code 
        name 

    warehouses
        id (PK)
        code
        name
        location
        capacity
        branch_id 
    
    platform_language 
        id 
        code 
        name enum ('DARI' , 'PASHTO' , 'ENGLISH' , 'ARABIC')

        

INVENTORY MODULE : 

    inventory_main_categories
        id (PK)
        title
        status enum('active','inactive') default 'active'

    inventory_sub_categories
        id
        title varchar
        main_category_id FK inventory_main_categories(id)
        status enum('active','inactive') default 'active'

    inventory_item_types
        id
        title
        status enum('active','inactive') default 'active'

    inventory_item_models
        id
        title - data example : model name ... 
        status enum('active','inactive') default 'active'

    inventory_items
        id (PK)
        sku                         varchar(100) unique  -- [{PREFIX-tenant-code}{YEAR}-{000001}] e.g., ADF24-0001
        reorder_level               numeric(10,2)
        description                 text
        components                  text,  -- or separate table if needed
        custom_fields               jsonb
        quality                     enum('high', 'medium', 'normal', 'low') default 'normal'
        branch_id                   FK branches(id)
        warehouse_id                FK warehouses(id)
        tenant_id                   FK tenant(id)
        created_by                  FK users(id)
        updated_by                  FK users(id)
        created_at
        updated_at

        -- Pricing/Purchase
        sales_currency_id           FK currencies(id)
        sales_unit_price            numeric(18,2)
        sales_unit                  FK - unit table (id)
        purchase_opening_date       date
        purchase_date               date
        purchase_unit               enum('piece', 'box', 'count', 'unit') - FK TO unit table 
        purchase_amount             numeric(18,2) not null default 0
        purchase_other_cost         numeric(18,2) default 0
        purchase_currency_id        FK currencies(id)
        purchase_exchange_rate      numeric(18,2) default 0


        -- Status/flags
        is_featured                 boolean default false
        is_hot                      boolean default false
        is_trending                 boolean default false
        is_wanted                   boolean default false
        repair_note                 varchar(512)
        status                      enum('new', 'damaged', 'expired', 'disposed', 'rented', 'reserved', 'repairing') default 'new'

    inventory_item_media
        id (PK)
        inventory_item_id           FK inventory_items(id)
        file_path                   varchar(255) not null
        title                       varchar(255)
        is_main                     boolean

    ## 🔑 Core Stock Flow Management

    stock_transactions
        id (PK)
        transaction_number          varchar(100) unique  -- e.g., "TRN24-000001"
        inventory_item_id           FK inventory_items(id)
        warehouse_id                FK warehouses(id)
        branch_id                   FK branches(id)
        type                        enum('stock_in', 'stock_out', 'adjustment', 'transfer_in', 'transfer_out', 'reservation','release', 'correction')

        reference_id                int nullable          -- link to sales order, purchase, etc.
        reference_type              varchar(50)           -- "sales_order", "purchase_order", "adjustment", etc.

        quantity                    numeric(18,2)
            -- positive for stock-in, transfer-in, adjustment-in; negative for stock-out, transfer-out, adjustment-out

        unit_cost                   numeric(18,2)
        currency_id                 FK currencies(id)
        exchange_rate               numeric(18,2)

        note                        text
        created_by                  FK users(id)
        created_at                  timestamptz default now()
        updated_at                  timestamptz default now()

### Notes:
- All *stock-in* events (purchases, production, returns, transfers received) are `type='stock_in'` or `'transfer_in'`, quantity is positive.
- All *stock-out* events (sales, disposals, internal usages, transfers sent) are `type='stock_out'` or `'transfer_out'`, quantity is negative.
- Adjustments (due to audit, correction) use `type='adjustment'` with positive/negative quantity.
- Transfer can be handled by paired records: `transfer_out` at source warehouse, `transfer_in` at destination.
- Calculate current stock by: **SUM(quantity) FROM stock_transactions WHERE inventory_item_id = ? AND warehouse_id = ?**
- Add indexes/index by (inventory_item_id, warehouse_id) for fast aggregation.

---

### Optionally, for reservations/dedicated quantities:

**inventory_reservations**
    id (PK)
    inventory_item_id           FK inventory_items(id)
    warehouse_id                FK warehouses(id)
    reserved_quantity           numeric(18,2)
    reserved_for                varchar(100) -- e.g., linked order id
    status                      enum('active','released','cancelled')
    created_at
    updated_at

---

### Example Use-Cases

- **Stock-In (Purchase):** Insert into `stock_transactions` with `type='stock_in'`, positive quantity linked to purchase order.
- **Stock-Out (Sales):** Insert into `stock_transactions` with `type='stock_out'`, negative quantity linked to sales order.
- **Adjustment:** Insert into `stock_transactions` with `type='adjustment'`, qty +/-, link to adjustment reference.
- **Transfer:** Insert two records: `type='transfer_out'` (from warehouse, negative qty), `type='transfer_in'` (to warehouse, positive qty).

---

**Never** mutate a 'quantity' field directly. Use transaction logs for full auditability and real-time accuracy.

---



































































======================================================================================================================================================================









general feature: 
    users 
        id 
        etc... 

    tenant 
        id 
        code 
        name 
        detail... 

    branch
        id 
        code 
        name 
        .. 
    warehouse 
        id 
        code 
        name 
        location
        capacity 

    Currency
        id 
        name 
        code 

core feature: 
    inventory_main_category 
        id 
        title 
        status enum [active,inactive] default active
        tenant_id FK tenant table 
        created_by FK user table 
        updated_by FK user table 
        created_at
        updated_at

    inventory_item_sub_category 
        id 
        title 
        main_category_id FK 

        status enum [active,inactive] default active
        tenant_id FK tenant table 
        created_by FK user table 
        updated_by FK user table 
        created_at
        updated_at

    inventory_item_types 
        id 
        title 
        status enum [active,inactive] default active
        tenant_id FK tenant table 
        created_by FK user table 
        updated_by FK user table 
        created_at
        updated_at
    
    inventory_item_model
        id 
        title 
        status enum [active,inactive] default active
        tenant_id FK tenant table 
        created_by FK user table 
        updated_by FK user table 
        created_at
        updated_at

    iventory_item
        id 
        sku                            varchar(100) unique, - autogenerated [{ADFSI}{YEAR}-001] - ADF26-001 , ADF26-002  aldubai stock item 
        name                           varchar(255) not null,

        image                          varchar(255), 
        quantity                       numeric(18,2) default 0,
        reserved_quantity              numeric(18,2) default 0,
        reorder_level                  numeric(10,2),

        sales_currency_id              integer references currencies(id),
        sales_unit_price               numeric(18,2),
        
        purchase_opening_date          date,
        purchase_date                  date,
        purchase_unit                  enum (piece,box, count, unit)   - UNIT COST 
        purchase_amount                numeric(18,2) not null default 0,
        purchase_other_cost            numeric(18,2) default 0,
        purchase_currency_id           FK currency table 
        purchase_exchange_rate         numeric(18,2) default 0,
        description                    text,
        components                     text, nullable 
        custom_fields                  jsonb, -- for custom dynamic fields
        quality                        enum (high, low, medium, normal) - default normal 
        branch_id                      FK branches(id),
        warehouse_id                   FK warehouse ,
        
        is_featured                    bool true, false 
        is_hot                         bool true, false 
        is_trending                    bool true, false 
        is_wanted                      bool true, false 

        repair_note                    varchar (512)
        status                         enum(50), -- e.g., new, damaged, expired, disposed, rented,reserved , darning (repair) 
        tenant_id FK tenant table 
        created_by FK user table 
        updated_by FK user table 
        created_at
        updated_at

    inventory_item_media:
        id                          serial primary key,
        inventory_item_id           integer references inventory_items(id) not null,
        file_path                   varchar(255) not null, -- file path or URL to the image
        title                       varchar(255),


    inventory_item_transaction 
        id 
        transaction_number -            transaction number (e.g., TRN26-0001)
        transaction_type -              enum (stock_in , stock_out)
        type - enum:                    rental, sales_order, procurement(purchase_order), 

        quantity -                      quantity of the inventory item
        unit_cost -                     unit price of the inventory item
        other_cost -                    other cost of the inventory item
        unit_cost_exchange_rate -                 exchange rate of the currency
        unit_cost_currency_id -                   foreign key to currencies table



        warehouse_id - foreign key to inventory_locations table
        inventory_item_id - foreign key to inventory_items table
        purchase_order_id - foreign key to purchase_orders table -  
        branch_id - foreign key to branches table



    inventory_item_ajustment
        id 
        inventory_item_id FK inventory_item_id
        type - enum: add, subtract
        quantity - integer 
        note - text
        adjustment_by - foreign key to users table
        adjustment_attachment - varchar(255)

        

# sales order request
# sales return




