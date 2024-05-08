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

        redNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'RedPotion'")).scalar()
        greenNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'GreenPotion'")).scalar()
        blueNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'BluePotion'")).scalar()
        healingNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'HealingPotion'")).scalar()
        fireNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'FirePotion'")).scalar()
        oceanNum = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(quantity), 0) FROM ledger WHERE sku = 'OceanPotion'")).scalar()


        potions = connection.execute(sqlalchemy.text("SELECT red,blue,green FROM potions"))

        if redNum > 0:
            catalog.append(
                    {
                        "sku": "RedPotion",
                        "name": "red potion",
                        "quantity": redNum,
                        "price": 50,
                        "potion_type": [100, 0, 0, 0]
                    }
            )

        if greenNum > 0:
            catalog.append(
                    {
                        "sku": "GreenPotion",
                        "name": "green potion",
                        "quantity": greenNum,
                        "price": 50,
                        "potion_type": [0, 100, 0, 0]
                    }
            )

        if blueNum > 0:
            catalog.append(
                    {
                        "sku": "BluePotion",
                        "name": "blue  potion",
                        "quantity": blueNum,
                        "price": 50,
                        "potion_type": [0, 0, 100, 0]
                    }
            )

        if healingNum > 0:
            catalog.append(
                    {
                        "sku": "HealingPotion",
                        "name": "healing potion",
                        "quantity": healingNum,
                        "price": 50,
                        "potion_type": [25, 25, 50, 0]
                    }
            )

        if fireNum > 0:
            catalog.append(
                    {
                        "sku": "FirePotion",
                        "name": "fire potion",
                        "quantity": fireNum,
                        "price": 50,
                        "potion_type": [75, 13, 12, 0]
                    }
            )

        if oceanNum > 0:
            catalog.append(
                    {
                        "sku": "OceanPotion",
                        "name": "ocean  potion",
                        "quantity": oceanNum,
                        "price": 50,
                        "potion_type": [0, 25, 75, 0]
                    }
            )

    return catalog

