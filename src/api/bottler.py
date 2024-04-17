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
        
        #get num of color ml and potions
        numRed = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        numGreen = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        numBlue = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
        numRedMl = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        numGreenMl = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        numBlueMl = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()

        for potion in potions_delivered:
            quantity = potion.quantity
            type = potion.potion_type

            #check potion type then subtract ml and add potions
            if(type == [100,0,0,0]):
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {numRed + quantity}"))
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {numRedMl - (quantity * 100)}"))

            if(type == [0,100,0,0]):
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {numGreen + quantity}"))
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {numGreenMl - (quantity * 100)}"))
            if(type == [0,0,100,0]):
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_potions = {numBlue + quantity}"))
                connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {numBlueMl - (quantity * 100)}"))
        

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
    with db.engine.begin() as connection:
        redMl = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        greenMl = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        blueMl = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()

        redNum = 0
        greenNum = 0
        blueNum = 0
        bottle_plan = []

        #if more than 100ml of red, order potions
        while redMl > 100:
             redMl -= 100
             redNum += 1
        if(redNum > 0):
            bottle_plan.append(
                {
                    "potion_type": [100, 0, 0, 0],
                    "quantity": redNum
                })
            
        #if more than 100ml of green, order potions
        while greenMl > 100:
             greenMl -= 100
             greenNum += 1
        if(greenNum > 0):
            bottle_plan.append(
                {
                    "potion_type": [0, 100, 0, 0],
                    "quantity": greenNum
                })
            
        #if more than 100ml of blue, order potions
        while blueMl > 100:
             blueMl -= 100
             blueNum += 1
        if(blueNum > 0):
            bottle_plan.append(
                {
                    "potion_type": [0, 0, 100, 0],
                    "quantity": blueNum
                })
            
    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())

