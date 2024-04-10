from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    potionNum = 0
    with db.engine.begin() as connection:
        potionNum = connection.execute(sqlalchemy.text("SELECT num_green_potion FROM global_inventory")).scalar()


        
    if potionNum > 1:
        return [
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            ]

