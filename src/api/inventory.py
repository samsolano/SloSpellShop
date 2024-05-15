from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """

    with db.engine.begin() as connection:
        Ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku LIKE '%Ml%'")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'Gold'")).scalar()
        total = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku LIKE '%Potion%'")).scalar()


    return {"number_of_potions": total, "ml_in_barrels": Ml, "gold": gold}

i = 0

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    if(i == 0):
         i += 1
         return {
        "potion_capacity": 0,
        "ml_capacity": 1
        }
        
    if(i != 0):
         return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }


   

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """    

    return "OK"
