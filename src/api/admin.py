from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE TABLE ledger"))
        connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES ('Gold', 100)"))
        # connection.execute(sqlalchemy.text("INSERT INTO ledger (sku, quantity) VALUES ('RedPotion', :quantity),('GreenPotion', :quantity),('BluePotion', :quantity),('HealingPotion', :quantity),('OceanPotion', :quantity),('FirePotion', :quantity),('RedMl', :quantity),('GreenMl', :quantity),('BlueMl', :quantity),('Gold', 100)"),
        #                        [{"quantity": 0}])


    return "OK"

