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


# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
    "potion_capacity": 1,
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
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            "UPDATE capacity SET potion_capacity = capacity.potion_capacity + :potionCap, ml_capacity = capacity.ml_capacity + :mlCap"),
                           [{"potionCap": capacity_purchase.potion_capacity * 50, "mlCap": capacity_purchase.ml_capacity * 10000}])
        
        connection.execute(sqlalchemy.text(
            "INSERT INTO ledger (sku, quantity) VALUES (:gold, :gold_spent)"),
                [{"gold": 'Gold', "gold_spent": (-1 * capacity_purchase.potion_capacity * 1000) + (capacity_purchase.ml_capacity * 1000 * -1)}])

    return "OK"
