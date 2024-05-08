from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    
    # Determine the column to sort by based on the `sort` parameter
    if sort_col is search_sort_options.customer_name:
        order_by = db.customer.c.name
    elif sort_col is search_sort_options.item_sku:
        order_by = db.cart_item.c.item
    elif sort_col is search_sort_options.line_item_total:
        order_by = db.cart_item.c.quantity
    elif sort_col is search_sort_options.timestamp:
        order_by = db.cart_item.c.created_at
    else:
        # If an invalid sorting option is provided, raise an assertion error
        assert False

    # Construct the SQL query
    stmt = (
        sqlalchemy.select(
            db.customer.c.name,
            db.cart_item.c.item,
            db.cart_item.c.quantity,
            db.cart_item.c.created_at
        )
        .limit(5)
        .offset(0)
        .order_by(order_by, db.cart_item.c.created_at)
    )

    with db.engine.begin() as connection: 
        if customer_name != "":
            # customer_name = connection.execute(sqlalchemy.text("SELECT name FROM customer WHERE name = :custName"), [{"custName":new_cart.customer_name }]).scalar()
            stmt = stmt.where(db.customer.c.name.ilike(f"%{customer_name}%"))

        if potion_sku != "":
            stmt = stmt.where(db.cart_item.c.item.ilike(f"%{potion_sku}%"))


    # Execute the SQL query
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json_data = []
        # Fetch the results row by row and construct JSON data
        for row in result:
            json_data.append(
            {
                "line_item_id": row.cart_id,
                "item_sku": f"{row.quantity} {row.item}",
                "customer_name":row.name ,
                "line_item_total":(row.quantity * 50),
                "timestamp": row.created_at,
            }
        )

    # Return the JSON data
    return json_data


    # return {
    #     "previous": "",
    #     "next": "",
    #     "results": [
    #         {
    #             "line_item_id": 1,
    #             "item_sku": "1 oblivion potion",
    #             "customer_name": "Scaramouche",
    #             "line_item_total": 50,
    #             "timestamp": "2021-01-01T00:00:00Z",
    #         }
    #     ],
    # }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"

#{int: cart_id, {sku: str : quantity: int }}
cart = {} 
cartNum = 0

@router.post("/")
def create_cart(new_cart: Customer):
    """ """

    # 1. put customer information into the customer table with a unique id
    # 2. check if the customer exists if not then create one
    # 3. then create a cart row with the associated customer

    response = {}

    with db.engine.begin() as connection: 

        # exists = connection.execute(sqlalchemy.text("SELECT cu_id FROM customer WHERE name = :custName AND class = :custClass AND level = :custLevel"),
        #                         [{"custName":new_cart.customer_name , "custClass": new_cart.character_class, "custLevel": new_cart.level}])


        # if(exists == None):
        connection.execute(sqlalchemy.text("INSERT INTO customer (name, class, level) VALUES (:custName, :custClass, :custLevel)"),
                                [{"custName":new_cart.customer_name , "custClass": new_cart.character_class, "custLevel": new_cart.level}])


        customerid = connection.execute(sqlalchemy.text("SELECT cu_id FROM customer WHERE name = :custName"), [{"custName":new_cart.customer_name }]).scalar()

        connection.execute(sqlalchemy.text("INSERT INTO cart (cu_id) VALUES (:customerID)"), [{"customerID": customerid}])

        cartid = connection.execute(sqlalchemy.text("SELECT cart_id FROM cart WHERE cu_id = :custID"), [{"custID":customerid }]).scalar()

    response['cart_id'] = str(cartid)
    return response


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    # 1. get associated cart id then find item sku and put the quantity wanted accordingly

    with db.engine.begin() as connection: 
        connection.execute(sqlalchemy.text("INSERT INTO cart_item (cart_id, item, quantity) VALUES (:cartID, :name, :quant)"), 
                           [{"cartID": cart_id, "name": item_sku , "quant": cart_item.quantity}])

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """

    # get all of the items in that cart id
    # need to insert into ledger negative potions that are sold,and increase gold for num sold


    with db.engine.begin() as connection:
        table = connection.execute(sqlalchemy.text("SELECT item, quantity FROM cart_item WHERE cart_id = :cartID"), [{"cartID": cart_id}])
        totalPotions = 0

        for item, quantity in table:
            totalPotions += quantity
            connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:name, :quant)"), [{"name": item, "quant": -1 * quantity}])

        connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES ('Gold', :quant)"), [{"quant": totalPotions * 50}])

    return {"total_potions_bought": totalPotions, "total_gold_paid": (50 * totalPotions)}




# TO DO:
#   still need to check if customer already exists in customer table inside of create_cart function