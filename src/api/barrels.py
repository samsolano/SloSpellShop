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

# need to fix catalog, bottling plan, wholesale plan, 

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int


#check barrels and update ml, decrease gold based on delivered barrels
#
@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    with db.engine.begin() as connection:
    #get current ml
        greenMl = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        redMl = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        blueMl = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        purchasePrice = 0

        #gets new ml values for potion color
        for barrel in barrels_delivered:
            # for red barrel
            if barrel.potion_type == [1,0,0,0]:
                redMl += (barrel.ml_per_barrel * barrel.quantity)
            # for green barrel
            elif barrel.potion_type == [0,1,0,0]:
                greenMl += (barrel.ml_per_barrel * barrel.quantity)
            # for blue barrel
            elif barrel.potion_type == [0,0,1,0]:
                blueMl += (barrel.ml_per_barrel * barrel.quantity)

            purchasePrice += (barrel.price * barrel.quantity)

        #update ml
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {redMl} "))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {greenMl} "))
        connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {blueMl} "))

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

        numRedPotions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        numGreenPotions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        numBluePotions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar()

        purchase_plan = []

        lessRed = numRedPotions < 10
        lessGreen = numGreenPotions < 10
        lessBlue = numBluePotions < 10


        for barrel in wholesale_catalog:
            #red
            if ((barrel.potion_type == [1,0,0,0]) and (barrel.price < gold) and (lessRed)):
                gold -= barrel.price

                purchase_plan.append({
                                        "sku": barrel.sku,
                                        "quantity": 1
                                    })
            #green    
            if ((barrel.potion_type == [0,1,0,0]) and (barrel.price < gold) and (lessGreen)):
                gold -= barrel.price

                purchase_plan.append({
                                        "sku": barrel.sku,
                                        "quantity": 1
                                    })
            #blue    
            if ((barrel.potion_type == [0,0,1,0]) and (barrel.price < gold) and (lessBlue)):
                gold -= barrel.price

                purchase_plan.append({
                                        "sku": barrel.sku,
                                        "quantity": 1
                                    })
                
                
        return purchase_plan
                
            




