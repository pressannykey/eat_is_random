from db.models import ZoonPlaces, ZoonPlacesInfo, ZoonDishes
from db.base import Session

session = Session()


def add_restaurant(rest_info):
    zoon_place = ZoonPlaces(
        zoon_place_name=rest_info["name"],
        zoon_place_url=rest_info["url"],
        lng=float(rest_info["lng"]),
        lat=float(rest_info["lat"]),
    )

    existing_place = (
        session.query(ZoonPlaces)
        .filter(ZoonPlaces.zoon_place_url == zoon_place.zoon_place_url)
        .first()
    )
    if not existing_place:
        session.add(zoon_place)
        session.commit()


def add_restaurant_info(info, restaurant: ZoonPlaces):
    if info["original_link"]:
        if type(info["original_link"]) == list:
            url = info["original_link"][0]
        else:
            url = info["original_link"]
    else:
        url = ""

    zoon_place_info = ZoonPlacesInfo(
        zoon_place_id=restaurant.zoon_place_id,
        rating=float(info["rating"]),
        schedule=info["schedule"],
        price_range=info["price_range"],
        phone_number=info["phone_number"],
        original_link=url,
        adress=info["adress"],
        # metro_stations=info["metro_stations"],
        # rayons=info["rayons"],
    )
    session.add(zoon_place_info)
    session.commit()


def add_dish(dish, restaurant):
    zoon_dish = ZoonDishes(
        description=dish["description"],
        title=dish["title"],
        category_url=dish["category_url"],
        price=dish["price"],
        zoon_place=restaurant,
    )

    existing_dish = (
        session.query(ZoonDishes).filter(ZoonDishes.title == zoon_dish.title).first()
    )

    if not existing_dish:
        session.add(zoon_dish)
        session.commit()


def get_restaurants():
    restaurants = session.query(ZoonPlaces).all()
    print(len(restaurants))
    return restaurants


def get_not_parsed_restaurants():
    restaurants_query = (
        session.query(ZoonPlaces)
        .outerjoin(ZoonPlacesInfo)
        .filter(ZoonPlacesInfo.zoon_places_info_id == None)
    )

    restaurants = restaurants_query.all()
    print(len(restaurants))

    return restaurants
