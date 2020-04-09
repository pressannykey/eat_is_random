from db.models import ZoonPlaces, ZoonPlacesInfo, ZoonDishes
from db.base import Session

session = Session()


def add_restaurant(rest_info):
    zoon_place = ZoonPlaces(zoon_place_name=rest_info["name"], zoon_place_url=rest_info["url"])
    session.add(zoon_place)
    session.commit()


def add_restaurant_info(info, restaurant: ZoonPlaces):
    url = info["original_link"][0] if info["original_link"] else ""
    zoon_place_info = ZoonPlacesInfo(
        zoon_place_id=restaurant.zoon_place_id,
        rating=float(info["rating"]),
        schedule=info["schedule"],
        price_range=info["price_range"],
        phone_number=info["phone_number"],
        original_link=url,
        adress=info["adress"]
    )
    session.add(zoon_place_info)
    session.commit()


def add_dish(dish, restaurant):
    zoon_dish = ZoonDishes(
        description=dish["description"],
        title=dish["title"],
        category_url=dish["category_url"],
        price=dish["price"],
        zoon_place=restaurant
    )
    session.add(zoon_dish)
    session.commit()


def get_restaurants():
    restaurants = session.query(ZoonPlaces).all()
    print(len(restaurants))
    return restaurants
