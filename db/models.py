from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Table, orm)

from db.base import Base


class Resources(Base):
    __tablename__ = "resources"

    resource_id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)


class CrawlingInfo(Base):
    __tablename__ = "crawling_info"

    crawling_info_id = Column(Integer, primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.resource_id"))
    crawl_start_time = Column(DateTime)
    crawl_end_time = Column(DateTime)
    status = Column(String)

    resource = orm.relationship(Resources)


class ZoonPlaces(Base):
    __tablename__ = "zoon_places"

    zoon_place_id = Column(Integer, primary_key=True)
    zoon_place_name = Column(String)
    zoon_place_url = Column(String, unique=True, nullable=False)
    lat = Column(Float)
    lng = Column(Float)

    zoon_dishes = orm.relationship("ZoonDishes")

    def __str__(self):
        return f"ZoonPlace {self.zoon_place_name} {self.zoon_place_url}"


class ZoonDishes(Base):
    __tablename__ = "zoon_dishes"

    zoon_dish_id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category_url = Column(String)
    price = Column(String)
    zoon_place_id = Column(Integer, ForeignKey("zoon_places.zoon_place_id"))

    zoon_place = orm.relationship("ZoonPlaces", back_populates="zoon_dishes")

    def __str__(self):
        return f"zoon dish {self.title} {self.price}"


class ZoonPlacesInfo(Base):
    __tablename__ = "zoon_places_info"

    zoon_places_info_id = Column(Integer, primary_key=True)
    zoon_place_id = Column(Integer, ForeignKey("zoon_places.zoon_place_id"))
    phone_number = Column(String)
    adress = Column(String)
    price_range = Column(String)
    # TODO: Перенести эти данные в отдельную таблицу
    # metro_stations = Column(Array(String))
    # rayons = Column(Array(String))
    schedule = Column(String)
    original_link = Column(String)
    rating = Column(Float)

    zoon_place = orm.relationship(ZoonPlaces)

    def __str__(self):
        return f"ZoonPlacesInfo {self.zoon_place.zoon_place_name} {self.rating}"


class Responses(Base):
    __tablename__ = "responses"

    response_id = Column(Integer, primary_key=True)
    response_time = Column(DateTime)
    query_location = Column(String)
    query_dish = Column(String)
    zoon_place_id = Column(Integer, ForeignKey("zoon_places.zoon_place_id"))
    zoon_dish_id = Column(Integer, ForeignKey("zoon_dishes.zoon_dish_id"))

    zoon_place = orm.relationship(ZoonPlaces)
    zoon_dish = orm.relationship(ZoonDishes)
