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
    #get new ml and insert into ledger
    #update and decrease gold into ledger

        purchasePrice = 0
        Ml = 0
        name = ""

        #gets new ml values for potion color
        for barrel in barrels_delivered:
            # for red barrel
            if barrel.potion_type == [1,0,0,0]:
                Ml = (barrel.ml_per_barrel * barrel.quantity)
                name = "RedMl"
            # for green barrel
            elif barrel.potion_type == [0,1,0,0]:
                Ml = (barrel.ml_per_barrel * barrel.quantity)
                name = "GreenMl"
            # for blue barrel
            elif barrel.potion_type == [0,0,1,0]:
                Ml = (barrel.ml_per_barrel * barrel.quantity)
                name = "BlueMl"

            purchasePrice += (barrel.price * barrel.quantity)

            connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:sku, :quantity)"), 
                            [{"sku":name, "quantity": Ml }])



        connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:sku, :quantity)"), 
                               [{"sku": "Gold", "quantity": -1 * purchasePrice}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        #check ml if less than 300 then buy stuff

        redMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'RedMl'")).scalar()
        greenMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'GreenMl'")).scalar()
        blueMl = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'BlueMl'")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'Gold'")).scalar()
        spent = 0

        purchase_plan = []

        # lessRed = redMl < 1000
        # lessGreen = greenMl < 1000
        # lessBlue = blueMl < 1000

        for barrel in wholesale_catalog:
            if ((barrel.price < gold) and barrel.price > 65):
                gold -= barrel.price
                spent += barrel.price
                purchase_plan.append({
                                        "sku": barrel.sku,
                                        "quantity": 1
                                    })
                
        connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES (:sku, :quantity)"),
                               [{"sku": "Gold", "quantity": -spent }])
            
                
                
        return purchase_plan
    

    # DO: need logic for quantity of barrels in purchase plan instead of just 1