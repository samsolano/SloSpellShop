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

            connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quant WHERE red = :red AND green = :green AND blue = :blue"),
                                [{"quant": deliverQuantity, "red": type[0], "green": type[1], "blue": type[2] }])
            
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :redUsed, num_green_ml = num_green_ml - :greenUsed, num_blue_ml = num_blue_ml - :blueUsed"),
                               [{"redUsed": type[0] ,"greenUsed": type[1] ,"blueUsed": type[2]}])


            # #check potion type then subtract ml and add potions
            # if(type == [100,0,0,0]):
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {numRed + quantity}"))
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {numRedMl - (quantity * 100)}"))

            # if(type == [0,100,0,0]):
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {numGreen + quantity}"))
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {numGreenMl - (quantity * 100)}"))
            # if(type == [0,0,100,0]):
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_potions = {numBlue + quantity}"))
            #     connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {numBlueMl - (quantity * 100)}"))
        

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

        bottle_plan = []
        potions = connection.execute(sqlalchemy.text("SELECT * FROM potions"))

        for potion in potions:
            haveRed = redMl > (redNeeded:= connection.execute(sqlalchemy.text("SELECT red FROM potions")).scalar())
            haveGreen = greenMl > (greenNeeded:= connection.execute(sqlalchemy.text("SELECT green FROM potions")).scalar())
            haveBlue = blueMl > (blueNeeded:= connection.execute(sqlalchemy.text("SELECT blue FROM potions")).scalar())

            if(haveRed and haveGreen and haveBlue):
                redMl -= redNeeded
                greenMl -= greenNeeded
                blueMl -= blueNeeded
                bottle_plan.append(
                {
                    "potion_type": [redNeeded, greenNeeded, blueNeeded, 0],
                    "quantity": 1
                })
            

        # #if more than 100ml of red, order potions
        # while redMl > 100:
        #      redMl -= 100
        #      redNum += 1
        # if(redNum > 0):
        #     bottle_plan.append(
        #         {
        #             "potion_type": [100, 0, 0, 0],
        #             "quantity": redNum
        #         })
            
        # #if more than 100ml of green, order potions
        # while greenMl > 100:
        #      greenMl -= 100
        #      greenNum += 1
        # if(greenNum > 0):
        #     bottle_plan.append(
        #         {
        #             "potion_type": [0, 100, 0, 0],
        #             "quantity": greenNum
        #         })
            
        # #if more than 100ml of blue, order potions
        # while blueMl > 100:
        #      blueMl -= 100
        #      blueNum += 1
        # if(blueNum > 0):
        #     bottle_plan.append(
        #         {
        #             "potion_type": [0, 0, 100, 0],
        #             "quantity": blueNum
        #         })
            
    return bottle_plan

if __name__ == "__main__":
    print(get_bottle_plan())

