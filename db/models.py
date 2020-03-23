from sqlalchemy import (Column, BigInteger, String, ForeignKey, DateTime)
from sqlalchemy import orm
from db.base import Base


class Resources(Base):
    """
    CREATE TABLE resources (
      resource_id bigint,
      name text,
      url text
    );
    """
    __tablename__ = 'resources'
    resource_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    url = Column(String)


class Crawling_info(Base):
    """
    CREATE TABLE crawling_info (
        crawling_info_id bigint,
        resource_id bigint REFERENCES resources(resource_id),
        crawl_start_time timestamp,
        crawl_end_time timestamp,
        status text
    );
    """
    __tablename__ = "crawling_info"
    crawling_info_id = Column(BigInteger, primary_key=True)
    resource_id = Column(BigInteger, ForeignKey("resources.resource_id"))
    crawl_start_time = Column(DateTime)
    crawl_end_time = Column(DateTime)
    status = Column(String)

    resource = orm.relationship(Resources)


class Gastro_classes(Base):
    """
    CREATE TABLE gastro_classes (
        gastro_classes_id bigint,
        name text
    );
    """
    __tablename__ = "gastro_classes"
    gastro_classes_id = Column(BigInteger, primary_key=True)
    name = Column(String)


class Zoon_places(Base):
    """
    CREATE TABLE zoon_places (
        zoon_place_id bigint,
        zoon_place_name text,
    );
    """
    __tablename__ = "zoon_places"
    zoon_place_id = Column(BigInteger, primary_key=True)
    zoon_place_name = Column(String)


class Zoon_gastros(Base):
    """
    CREATE TABLE zoon_gastros (
        zoon_gastro_id bigint,
        name text,
        synonym_id REFERENCES zoon_gastros(name),
        gastro_classes_id FOREIGN KEY REFERENCES gastro_classes(gastro_classes_id)
    );
    """
    __tablename__ = "zoon_gastros"
    zoon_gastro_id = Column(BigInteger, primary_key=True)
    name = Column(String)
    synonym_id = Column(BigInteger, ForeignKey("zoon_gastros.zoon_gastro_id"))
    gastro_classes_id = Column(BigInteger, ForeignKey("gastro_classes.gastro_classes_id"))

    synonym = orm.relationship("Zoon_gastros")
    synonym = orm.relationship(Gastro_classes)


class Responses(Base):
    """
    CREATE TABLE responses (
        response_id bigint,
        response_time timestamp,
        query_location text,
        query_gastro text,
        zoon_place bigint REFERENCES zoon_places(zoon_place_id),
        zoon_gastro_id bigint REFERENCES zoon_gastros(zoon_gastro_id)
    );
    """
    __tablename__ = "responses"

    response_id = Column(BigInteger, primary_key=True)
    response_time = Column(DateTime)
    query_location = Column(String)
    query_gastro = Column(String)
    zoon_place_id = Column(BigInteger, ForeignKey("zoon_places.zoon_place_id"))
    zoon_gastro_id = Column(BigInteger, ForeignKey("zoon_gastros.zoon_gastro_id"))

    zoon_place = orm.relationship(Zoon_places)
    zoon_gastro = orm.relationship(Zoon_gastros)

class Zoon_menues(Base):
    """
    CREATE TABLE zoon_menues (
        zoon_place_id bigint REFERENCES zoon_places(zoon_place_id),
        zoon_gastro_id bigint REFERENCES zoon_gastros(zoon_gastro_id)
    );
    """
    __tablename__ = "zoon_menues"
    zoon_menu_id = Column(BigInteger, primary_key=True)
    zoon_place_id = Column(BigInteger, ForeignKey("zoon_places.zoon_place_id"))
    zoon_gastro_id = Column(BigInteger, ForeignKey("zoon_gastros.zoon_gastro_id"))

    zoon_place = orm.relationship(Zoon_places)
    zoon_gastro = orm.relationship(Zoon_gastros)
