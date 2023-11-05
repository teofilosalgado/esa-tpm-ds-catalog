# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime

from geoalchemy2 import load_spatialite_gpkg
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from shapely.geometry import Point, Polygon
from sqlalchemy import create_engine
from sqlalchemy.event import listen
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from scraper.models import Base, Product


class StringToGeometry:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("geometry"):
            string_vertices = adapter["geometry"].split(" ")
            float_vertices = [float(item) for item in string_vertices]
            tuple_vertices = [
                reversed(float_vertices[i : i + 2])
                for i in range(0, len(float_vertices), 2)
            ]
            points = [Point(*item) for item in tuple_vertices]
            polygon = Polygon(points)
            adapter["geometry"] = polygon

            return item
        else:
            raise DropItem(f"Missing geometry in {item} at {spider}")


class StringToDatetimePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get("acquisition_date") and adapter.get("stop_date"):
            new_acquisition_date = datetime.fromisoformat(adapter["acquisition_date"])
            adapter["acquisition_date"] = new_acquisition_date

            new_stop_date = datetime.fromisoformat(adapter["stop_date"])
            adapter["stop_date"] = new_stop_date

            return item
        else:
            raise DropItem(f"Missing date in {item} at {spider}")


class SQLitePipeline:
    def __init__(self):
        engine = create_engine("gpkg:///esa-tpm-ds-catalog.gpkg")
        listen(engine, "connect", load_spatialite_gpkg)
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        product = Product()
        product.spider = spider.name
        product.acquisition_date = item["acquisition_date"]
        product.stop_date = item["stop_date"]
        product.orbit = item["orbit"]
        product.orbit_direction = item["orbit_direction"]
        product.path = item["path"]
        product.row = item["row"]
        product.geometry = item["geometry"].wkt
        product.sensor_mode = item["sensor_mode"]
        product.product_type = item["product_type"]
        product.product_info_url = item["product_info_url"]
        product.product_download_url = item["product_download_url"]
        try:
            session.add(product)
            session.commit()
        except SQLAlchemyError:
            session.rollback()
            raise
        finally:
            session.close()
        return item
