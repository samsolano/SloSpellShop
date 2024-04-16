from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    catalog = []

    with db.engine.begin() as connection:
        redNum = connection.execute(sqlalchemy.text("SELECT num_red_potion FROM global_inventory")).scalar()
        greenNum = connection.execute(sqlalchemy.text("SELECT num_green_potion FROM global_inventory")).scalar()
        blueNum = connection.execute(sqlalchemy.text("SELECT num_blue_potion FROM global_inventory")).scalar()


        
    if redNum > 0:
        catalog.append(
                {
                    "sku": "RED_POTION",
                    "name": "red potion",
                    "quantity": redNum,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0]
                }
        )

    if greenNum > 0:
        catalog.append(
                {
                    "sku": "GREEN_POTION",
                    "name": "green potion",
                    "quantity": greenNum,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0]
                }
        )

    if blueNum > 0:
        catalog.append(
                {
                    "sku": "BLUE_POTION",
                    "name": "blue  potion",
                    "quantity": blueNum,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0]
                }
        )
    
    return catalog

