from db.models import ZoonDishes, ZoonPlaces, ZoonPlacesInfo
from db.base import engine
from dataclasses import dataclass
from pprint import pprint
from sqlalchemy import desc, join, select
from sqlalchemy import func as sa_func
from sqlalchemy.dialects import postgresql
from bot.selectors.user_input import get_user_input
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

        places = conn.execute(result).fetchall()

        return places


def get_places(dishes):
    c = PlacePicker()
    places = {}
    with engine.connect() as conn:
        # выбираем заведения по всем вариациям из ввода
        place_count = 0
        for dish in dishes:
            tmp_places = c.select_place(conn, dish)
            places.update({dish: tmp_places})
            # если нашли достаточное количество мест, повторно в базу не идем
            place_count += len(tmp_places)
            if place_count > 5:
                break
    return places


def place_handler(places, full_match):
    direct_match = False
    result_places = []
    if not places:
        return result_places, direct_match
    direct_match_places = places[full_match]
    if direct_match_places:
        direct_match = True
        result_places = direct_match_places
        return result_places, direct_match
    for value in places.values():
        result_places.extend(value)
    return result_places, direct_match


def place_output(places, direct_match):
    if not places:
        answer = 'Ничего не нашлось'
        return answer
    text = '''{} заведение: 
{} с рейтингом {}, по адресу: {}. Тел: {}
В меню: {}'''
    place = random.choice(places)
    dishes = ", ".join(place[-1])
    if direct_match:
        answer = text.format(
            'Мы нашли', place[1], place[2], place[3], place[4], dishes)
    else:
        answer = text.format('Точного совпадения не нашлось.\nВозможно, вам подойдет',
                             place[1], place[2], place[3], place[4], dishes)
    return answer


def get_place_by_dish(user_input):
    dish, dishes = get_user_input(user_input)
    all_places = get_places(dishes)
    places, direct_match = place_handler(all_places, dish)
    answer = place_output(places, direct_match)
    return answer


if __name__ == "__main__":
    get_place_by_dish(input('Введите блюдо: '))
