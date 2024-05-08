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

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


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

        exists = connection.execute(sqlalchemy.text("SELECT cu_id FROM customer WHERE name = :custName AND class = :custClass AND level = :custLevel"),
                                [{"custName":new_cart.customer_name , "custClass": new_cart.character_class, "custLevel": new_cart.level}])


        if(exists == None):
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

    # 


    with db.engine.begin() as connection:
        redNum = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()

    # totalPotions = 0

    # with db.engine.begin() as connection:
    #     redNum = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
    #     greenNum = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
    #     blueNum = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
    #     gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()
    #     currCart = cart[cart_id]


    #     for sku in currCart:
    #         if sku == "RED_POTION":
    #             redNum -= currCart[sku]
    #             totalPotions += currCart[sku]
    #         elif sku == "GREEN_POTION":
    #             greenNum -= currCart[sku]
    #             totalPotions += currCart[sku]
    #         elif sku == "BLUE_POTION":
    #             blueNum -= currCart[sku]
    #             totalPotions += currCart[sku]



    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {redNum}"))
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {greenNum}"))
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_potions = {blueNum}"))
    #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold + (50 * totalPotions)}"))

    # return {"total_potions_bought": totalPotions, "total_gold_paid": (50 * totalPotions)}




# TO DO:
#   still need to check if customer already exists in customer table inside of create_cart function