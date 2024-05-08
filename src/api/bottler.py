from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
        

        # increase quantities on potions delivered and decrease ml
        for potion in potions_delivered:
            deliverQuantity = potion.quantity
            type = potion.potion_type


            # gets name of potion delivered
            name = connection.execute(sqlalchemy.text("SELECT name FROM potions WHERE red = :red AND green = :green AND blue = :blue"),
                                    [{"quant": deliverQuantity, "red": type[0], "green": type[1], "blue": type[2] }]).scalar()
            
            # inserts into ledger the name and quantity of new potion
            connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:sku, :quantity)"),
                               [{"sku":name, "quantity": 1}])
            
            # inserts into ledge the change in mL
            connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:redMl, :RedQuantity), (:greenMl, :GreenQuantity), (:blueMl, :BlueQuantity)"),
                                [{"redMl": "RedMl", "RedQuantity": -1 * deliverQuantity * type[0], "greenMl": "greenMl", "GreenQuantity": -1 * deliverQuantity * type[1], "blueMl": "BlueMl", "BlueQuantity": -1 * deliverQuantity * type[2]}])

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # get amount of Ml
    with db.engine.begin() as connection:
        redMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE name = 'RedMl'")).scalar()
        greenMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE name = 'GreenMl'")).scalar()
        blueMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE name = 'BlueMl'")).scalar()
        

        bottle_plan = []

        colors = connection.execute(sqlalchemy.text("SELECT red,blue,green FROM potions"))

        for red,blue,green in colors:

            if((redMl > red) and (greenMl > green) and (blueMl > blue)):
                redMl -= red
                greenMl -= green
                blueMl -= blue
                bottle_plan.append(
                {
                    "potion_type": [red, green, blue, 0],
                    "quantity": 1
                })
            
    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())

