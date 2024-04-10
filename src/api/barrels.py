from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
    #get current ml
        greenMl = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()

        newAmount = greenMl
        purchasePrice = 0
        for barrel in barrels_delivered:
            newAmount += barrel.ml_per_barrel
            purchasePrice += barrel.price

        #update ml
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {newAmount} "))

        #get current gold after purchase
        currentGold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar() - purchasePrice
        #update gold
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {currentGold} "))



    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)


    with db.engine.begin() as connection:

        #check number of potions, if less than 10 then order barrel and change gold amount

        numPotions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()


        barrel = wholesale_catalog[0]
        barrelPrice = barrel.price


        if numPotions < 10 and gold >= barrelPrice:
            currGold = gold - barrelPrice
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {currGold}"))
            return [
                {
                    "sku": "SMALL_GREEN_BARREL",
                    "quantity": 1,
                }
            ]

