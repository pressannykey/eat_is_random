from db.models import ZoonDishes, ZoonPlaces, ZoonPlacesInfo
from db.base import engine
from dataclasses import dataclass
from pprint import pprint
from sqlalchemy import desc, join, select
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql
from test import get_user_input
import random


@dataclass()
class PlacePicker:
    @staticmethod
    def select_place(conn, dish_title: str) -> ZoonPlacesInfo:
        prepared_dish_title = "%{}%".format(dish_title)

        zoon_dishes_filter = ZoonDishes.title.ilike(prepared_dish_title)

        columns = [
            ZoonPlaces.zoon_place_id,
            ZoonPlaces.zoon_place_name,
            sa_func.max(ZoonPlacesInfo.rating),
            ZoonPlacesInfo.adress,
            ZoonPlacesInfo.phone_number,
            sa_func.count(ZoonPlaces.zoon_place_id),
            sa_func.array_agg(ZoonDishes.title),
        ]

        joins = join(ZoonPlacesInfo, ZoonPlaces).join(ZoonDishes)

        filtered_places = select(
            columns, zoon_dishes_filter, from_obj=joins)

        result = filtered_places.group_by(ZoonPlaces.zoon_place_id, ZoonPlacesInfo.adress, ZoonPlacesInfo.phone_number).order_by(desc(
            sa_func.max(ZoonPlacesInfo.rating)), desc(sa_func.count(ZoonPlaces.zoon_place_id))).limit(10)

        zz = result.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        print(zz)

        places = conn.execute(result).fetchall()

        return places


def place_output(places):
    if not places:
        result = "Ничего не нашлось:("
        return result
    place = random.choice(places)
    dishes = ", ".join(place[-1])
    result = f'''Мы нашли заведение: 
{place[1]} с рейтингом {place[2]}, по адресу: {place[3]}. Тел: {place[4]}
В меню: {dishes}'''
    return result


def get_places(dishes):
    c = PlacePicker()
    places = []
    with engine.connect() as conn:
        # выбираем заведения по всем вариациям из ввода
        for dish in dishes:
            tmp_places = c.select_place(conn, dish)
            places.extend(tmp_places)
            # если нашли достаточное количество мест, повторно в базу не идем
            if len(places) > 5:
                break
    return places


def all_together():
    dishes = get_user_input()
    places = get_places(dishes)
    answer = place_output(places)
    print(answer)


if __name__ == "__main__":
    all_together()
