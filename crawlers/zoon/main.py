import typing as t
from dataclasses import dataclass

import requests
import yarl
from bs4 import BeautifulSoup

from crawlers.zoon.utils import get_html, parse_values, get_field_value


@dataclass
class Restaurant:
    db_id: int
    name: str
    url: yarl.URL


@dataclass
class RestaurantsInfo:
    db_id: int
    restaurant_id: int
    phone_number: str
    adress: str
    # rayons: t.List
    # metro_stations: t.List
    price_range: str
    schedule: str
    original_link: t.List[yarl.URL]
    rating: float


@dataclass
class Dish:
    db_id: int
    restaurant_id: int
    title: str
    description: str
    category_url: yarl.URL
    price: str


class DB_module:
    restaurant_id = 0
    restaurant_info_id = 0
    dish_id = 0

    dishes = []
    restaurants = []
    restaurants_info = []

    def add_restaurant(self, rest_info):
        self.restaurant_id += 1
        self.restaurants.append(Restaurant(
            self.restaurant_id, rest_info["name"], rest_info["url"]))

    def add_restaurant_info(self, info, restaurant):
        self.restaurant_info_id += 1
        self.restaurants_info.append(RestaurantsInfo(
            db_id=self.restaurant_info_id, restaurant_id=restaurant.db_id, **info))

    def add_dish(self, dish, restaurant):
        self.dish_id += 1
        self.dishes.append(
            Dish(db_id=self.dish_id, restaurant_id=restaurant.db_id, **dish))

    def get_restaurants(self):
        return self.restaurants


@dataclass
class Field:
    value_type: type
    # we have some cases with different selectors for one field
    css_selectors: t.List[str]
    attr: str = None


class Crawler:
    db_module = DB_module()

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
        }

        soup = BeautifulSoup(page, 'html.parser')
        all_rests = soup.select('div.service-description')

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
            "title": Field(value_type=str, css_selectors=['span.js-pricelist-title a', 'span.js-pricelist-title']),
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
                        self.db_module.add_restaurant(restaraunt)

                    break
                except(requests.RequestException, ValueError, NotImplementedError):
                    print('asdas')
                    tries += 1

            print('Усё')  # TODO: combinations_with_replacement with meaningful logging

    def crawl_restaurant(self):
        for restaurant in self.db_module.get_restaurants():
            print(restaurant)  # TODO: combinations_with_replacement with meaningful logging
            try:
                restaurant_page = get_html(f"{restaurant.url}menu", "GET")
            except(requests.RequestException, ValueError, NotImplementedError):
                print("Can't crawl: ", restaurant)  # TODO: combinations_with_replacement with meaningful logging
                continue

            soup = BeautifulSoup(restaurant_page, 'html.parser')

            rest_other_info = self.__parse_restaurants_info(soup)
            self.db_module.add_restaurant_info(rest_other_info, restaurant)

            dishes = self.__parse_restaurants_menu(soup)
            for dish in dishes:
                self.db_module.add_dish(dish, restaurant)

        tmp = [print(x) for x in self.db_module.restaurants_info]

    def start_crawl(self):
        # TODO: crawl_id = self.db_module.new_crawl()
        self.crawl_pages()
        self.crawl_restaurant()
        # TODO: self.db_module.end_crawl(crawl_id, "success")


if __name__ == "__main__":
    c = Crawler()
    c.start_crawl()
