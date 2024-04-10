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

    #assuming theres only green potions being delivered
    #potionList = potions_delivered[0]

    with db.engine.begin() as connection:
        for potion in potions_delivered:
            quant = potion.quantity
            numPotionsCurr = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar() + quant
            connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {numPotionsCurr}"))
        




        # #get current num of potions
        # numPotionsCurr = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        # for potion in potions_delivered:
        #     numPotionsCurr += 1
        # #update table for number of potions
        
###############################################################################################################################
        
         

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    #get amount of green potion Ml
    quant = 0
    with db.engine.begin() as connection:
        greenMl = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()

        while greenMl > 100:
            # get number of potions + 1
             numPotions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar() + 1

            # add potion number back into table
             connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {numPotions}"))

             greenMl -= 100
             quant += 1

        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {greenMl}"))

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": quant,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())

