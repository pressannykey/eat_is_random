import typing as t
import yarl

from bs4 import BeautifulSoup
from dataclasses import dataclass
from crawlers.zoon.utils import get_html, crawl_values, get_field_value


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

    def __getattr__(self, attr):
        return self

    def __call__(*args, **kwargs):
        return 1


@dataclass
class Field:
    value_type: type
    # we have some cases with different selectors for one field
    css_selectors: t.List[str]
    attr: str = None


class Crawler:
    db_module = DB_module()

    def get_page(self, num: int) -> str:
        url = 'https://spb.zoon.ru/restaurants/?action=list&type=service'
        data = {
            'search_query_form': 1,
            'sort_field': 'rating',
            'need[]': 'items',
            'page': num,
        }
        html = get_html(url, 'POST', data=data)
        return html

    def add_restaurants_to_db(self, page: str) -> None:
        rest_list = {
            "url": Field(value_type=yarl.URL, css_selectors=['div.H3>a'], attr='href'),
            "name": Field(value_type=str, css_selectors=['div.H3>a']),
        }

        soup = BeautifulSoup(page, 'html.parser')
        all_rests = soup.select('div.service-description')
        for rest in all_rests:
            rest_main_info = crawl_values(rest, rest_list)

            self.db_module.add_restaurant(rest_main_info)

    def add_restaurants_info_to_db(self, restaurant, soup) -> None:
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

        rest_other_info = crawl_values(soup, place_card)

        self.db_module.add_restaurant_info(rest_other_info, restaurant)

    def add_restaurants_menu_to_db(self, restaurant, soup) -> None:
        menu = {
            "description": Field(value_type=str, css_selectors=['span.js-pricelist-description']),
            "title": Field(value_type=str, css_selectors=['span.js-pricelist-title a', 'span.js-pricelist-title']),
            "category_url": Field(value_type=yarl.URL, css_selectors=['span.js-pricelist-title a'], attr='href'),
            "price": Field(value_type=str, css_selectors=['div.price-weight strong']),
        }

        # all_dishes is soup or []
        # пишем ли что-то в базу, если []?
        all_dishes = soup.select('div.pricelist-item-content')
        for dishes in all_dishes:
            dish = crawl_values(dishes, menu)

            self.db_module.add_dish(dish, restaurant)

    def start_crawl(self):
        crawl_id = self.db_module.new_crawl()
        for page_number in range(1, 3):
            page = self.get_page(page_number)
            if not page:
                return

            self.add_restaurants_to_db(page)

        for restaurant in self.db_module.get_restaurants():
            restaurant_page = get_html(f"{restaurant.url}menu", "GET")
            if not restaurant_page:
                continue
            soup = BeautifulSoup(restaurant_page, 'html.parser')

            self.add_restaurants_info_to_db(restaurant, soup)
            self.add_restaurants_menu_to_db(restaurant, soup)

        tmp = [print(x) for x in self.db_module.restaurants_info]
        # print()
        # tmp = [print(x) for x in self.db_module.dishes]
        self.db_module.end_crawl(crawl_id, "success")


if __name__ == "__main__":
    c = Crawler()
    c.start_crawl()
