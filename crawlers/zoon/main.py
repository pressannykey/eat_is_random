import typing as t
from dataclasses import dataclass

import requests
import yarl
from bs4 import BeautifulSoup

import sys
from pathlib import Path

file = Path(__file__).resolve()
root = file.parents[2]
sys.path.append(str(root))

from crawlers.zoon.utils import get_html, parse_values, get_field_value
from crawlers.zoon import db_module


@dataclass
class Field:
    value_type: type
    # можно изменить тип css_selectors на str, но оставим для случая, если данные лежат в разных селекторах
    css_selectors: t.List[str]
    attr: str = None


class Crawler:
    def __get_page(self, num: int) -> t.Optional[str]:
        url = 'https://spb.zoon.ru/restaurants/?action=list&type=service'
        data = {
            'search_query_form': 1,
            'sort_field': 'rating',
            'need[]': 'items',
            'page': num,
        }
        html = get_html(url, 'POST', data=data)

        return html

    @staticmethod
    def __parse_restaurants_from_page(page: str):
        rest_list = {
            "url": Field(value_type=yarl.URL, css_selectors=['div.H3>a'], attr='href'),
            "name": Field(value_type=str, css_selectors=['div.H3>a']),
            "lng": Field(value_type=float, css_selectors=[], attr='data-lon'),
            "lat": Field(value_type=float, css_selectors=[], attr='data-lat'),
        }

        soup = BeautifulSoup(page, 'html.parser')
        all_rests = soup.select('li.service-item')

        restaurants_ = [
            parse_values(rest, rest_list)
            for rest in all_rests
        ]

        return restaurants_
        

    def __parse_restaurants_info(self, soup) -> t.Any:
        """Clean parsing"""
        place_card = {
            "rating": Field(value_type=float, css_selectors=['span.rating-value']),
            "schedule": Field(value_type=str, css_selectors=['dd.upper-first>div']),
            # "metro_stations": Field(value_type=t.List[str], css_selectors=['div.address-metro>a']),
            # "rayons": Field(value_type=t.List[str], css_selectors=['div.mg-bottom-m a.invisible-link']),
            "price_range": Field(value_type=str, css_selectors=['div.time__price span']),
            "phone_number": Field(value_type=str, css_selectors=['div.oh span.js-phone'], attr='data-number'),
            "original_link": Field(value_type=t.List[yarl.URL], css_selectors=['div.service-website a'], attr='href'),
            "adress": Field(value_type=str, css_selectors=['address.iblock']),
        }

        rest_other_info = parse_values(soup, place_card)

        return rest_other_info

    def __parse_restaurants_menu(self, soup) -> t.List:
        """Clean parsing"""
        menu = {
            "description": Field(value_type=str, css_selectors=['span.js-pricelist-description']),
            "title": Field(value_type=str, css_selectors=['span.js-pricelist-title']),
            "category_url": Field(value_type=yarl.URL, css_selectors=['span.js-pricelist-title a'], attr='href'),
            "price": Field(value_type=str, css_selectors=['div.price-weight strong']),
        }

        # all_dishes is soup or []
        # пишем ли что-то в базу, если []?
        all_dishes = soup.select('div.pricelist-item-content')

        dishes = [
            parse_values(dishes, menu)
            for dishes in all_dishes
        ]

        return dishes

    def crawl_pages(self, page_counts: int = 3) -> None:
        for page_number in range(1, 3):
            print(page_number)  # TODO: combinations_with_replacement with meaningful logging
            tries = 0
            while tries < 2:
                try:
                    page = self.__get_page(page_number)
                    for restaraunt in self.__parse_restaurants_from_page(page):
                        print(restaraunt)
                        db_module.add_restaurant(restaraunt)

                    break
                except(requests.RequestException, ValueError, NotImplementedError):
                    print('ошибка')
                    tries += 1

            print('Усё')  # TODO: combinations_with_replacement with meaningful logging

    def crawl_restaurant(self):
        for restaurant in db_module.get_restaurants():
            print(restaurant)  # TODO: combinations_with_replacement with meaningful logging
            try:
                restaurant_page = get_html(f"{restaurant.zoon_place_url}menu", "GET")
            except(requests.RequestException, ValueError, NotImplementedError):
                print("Can't crawl: ", restaurant)  # TODO: combinations_with_replacement with meaningful logging
                continue

            soup = BeautifulSoup(restaurant_page, 'html.parser')

            rest_other_info = self.__parse_restaurants_info(soup)
            db_module.add_restaurant_info(rest_other_info, restaurant)

            dishes = self.__parse_restaurants_menu(soup)
            for dish in dishes:
                db_module.add_dish(dish, restaurant)

    def start_crawl(self):
        # TODO: crawl_id = db_module.new_crawl()
        self.crawl_pages()
        self.crawl_restaurant()
        # TODO: db_module.end_crawl(crawl_id, "success")


if __name__ == "__main__":
    c = Crawler()
    c.start_crawl()
