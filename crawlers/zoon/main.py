import typing as t
from dataclasses import dataclass

import time
import requests
import yarl
from bs4 import BeautifulSoup

import sys
from pathlib import Path

file = Path(__file__).resolve()
root = file.parents[2]
sys.path.append(str(root))

from crawlers.zoon import db_module
from crawlers.zoon.utils import get_html, parse_values, get_field_value


@dataclass
class Field:
    value_type: type
    # можно изменить тип css_selectors на str, но оставим для случая, если данные лежат в разных селекторах
    css_selectors: t.List[str]
    attr: str = None


class Crawler:
    URL = "https://spb.zoon.ru/restaurants/?action=list&type=service"

    place_type = {
        "бургерная": "m[5968445564288e27e4457a78]",
        "бар": "m[4f84a6c93c72dddc66000019]",
        "кофейня": "m[4f84a6e73c72dddc6600001a]",
        "суши-бар": "m[5228936340c088ae2a8b4591]",
        "пиццерия": "m[5200e4d5a0f302f06600000c]",
    }

    stop_places = [
        "burger king",
        "hesburger",
        "макдоналдс",
        "kfc",
        "mcdonald’s",
        "mcdonalds",
    ]

    def __get_page(self, place_type: str, num: int) -> t.Optional[str]:
        url = self.URL
        data = {
            place_type: 1,
            "search_query_form": 1,
            "sort_field": "rating",
            "need[]": "items",
            "page": num,
        }
        html = get_html(url, "POST", data=data)

        return html

    @staticmethod
    def __parse_restaurants_from_page(page: str) -> t.List[t.Dict[str, t.Any]]:
        rest_list = {
            "url": Field(value_type=yarl.URL, css_selectors=["div.H3>a"], attr="href"),
            "name": Field(value_type=str, css_selectors=["div.H3>a"]),
            "lng": Field(value_type=float, css_selectors=[], attr="data-lon"),
            "lat": Field(value_type=float, css_selectors=[], attr="data-lat"),
        }

        soup = BeautifulSoup(page, "html.parser")
        all_rests = soup.select("li.service-item")

        restaurants_ = [parse_values(rest, rest_list) for rest in all_rests]

        return restaurants_

    def __parse_restaurants_info(self, soup) -> t.Any:
        """Clean parsing"""
        place_card = {
            "rating": Field(value_type=float, css_selectors=["span.rating-value"]),
            "schedule": Field(value_type=str, css_selectors=["dd.upper-first>div"]),
            "metro_stations": Field(
                value_type=t.List[str], css_selectors=["div.address-metro>a"]
            ),
            "rayons": Field(
                value_type=t.List[str],
                css_selectors=["div.mg-bottom-m a.invisible-link"],
            ),
            "price_range": Field(
                value_type=str, css_selectors=["div.time__price span"]
            ),
            "phone_number": Field(
                value_type=str,
                css_selectors=["div.oh span.js-phone"],
                attr="data-number",
            ),
            "original_link": Field(
                value_type=t.List[yarl.URL],
                css_selectors=["div.service-website a"],
                attr="href",
            ),
            "adress": Field(value_type=str, css_selectors=["address.iblock"]),
        }

        rest_other_info = parse_values(soup, place_card)

        return rest_other_info

    def __parse_restaurants_menu(self, soup) -> t.List:
        """Clean parsing"""
        menu = {
            "description": Field(
                value_type=str, css_selectors=["span.js-pricelist-description"]
            ),
            "title": Field(value_type=str, css_selectors=["span.js-pricelist-title"]),
            "category_url": Field(
                value_type=yarl.URL,
                css_selectors=["span.js-pricelist-title a"],
                attr="href",
            ),
            "price": Field(value_type=str, css_selectors=["div.price-weight strong"]),
        }

        # all_dishes is soup or []
        all_dishes = soup.select("div.pricelist-item-content")

        dishes = [parse_values(dishes, menu) for dishes in all_dishes]

        return dishes

    def crawl_pages(self, place_type) -> None:
        page = 1
        print(page)
        while True:
            try:
                html = self.__get_page(place_type, page)
                page += 1

                # если ничего не подгрузилось, нужного элемента не будет на странице
                if '<div class="service-description">' not in html:
                    print("Страниц больше нет")
                    break

                for restaraunt in self.__parse_restaurants_from_page(html):
                    if restaraunt["name"].lower() not in self.stop_places:
                        print(restaraunt)
                        db_module.add_restaurant(restaraunt)

                if "Больше нет мест" in html:
                    print("Это была последняя страница")
                    break

            except (requests.RequestException, ValueError, NotImplementedError) as e:
                print("Ошибка", e)
                break

        print("Всё")  # TODO: combinations_with_replacement with meaningful logging

    def crawl_restaurant(self):
        for restaurant in db_module.get_not_parsed_restaurants():
            # TODO: combinations_with_replacement with meaningful logging
            for i in range(3):
                try:
                    restaurant_page = get_html(
                        f"{restaurant.zoon_place_url}menu", "GET"
                    )
                    print("Парсим ресторан ", restaurant)
                    end = False
                    break
                except (requests.RequestException, ValueError, NotImplementedError):
                    # TODO: combinations_with_replacement with meaningful logging
                    print("Can't crawl: ", restaurant)
                    if i == 2:
                        print("Все еще забанены:( вырубай")
                        end = True
                    time.sleep(10)
                    continue
            if end:
                continue
            soup = BeautifulSoup(restaurant_page, "html.parser")

            rest_other_info = self.__parse_restaurants_info(soup)
            db_module.add_restaurant_info(rest_other_info, restaurant)

            dishes = self.__parse_restaurants_menu(soup)
            for dish in dishes:
                db_module.add_dish(dish, restaurant)

    def start_crawl(self):
        # TODO: crawl_id = db_module.new_crawl()
        for values in self.place_type.values():
            self.crawl_pages(values)
        self.crawl_restaurant()
        # TODO: db_module.end_crawl(crawl_id, "success")


if __name__ == "__main__":
    c = Crawler()
    c.start_crawl()
