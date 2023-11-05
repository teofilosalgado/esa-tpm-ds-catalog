from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "product"
    # Metadata columns
    id = Column(Integer, primary_key=True)
    spider = Column(Text())

    # Information columns
    acquisition_date = Column("acquisition_date", DateTime(timezone=True))
    stop_date = Column("stop_date", DateTime(timezone=True))
    orbit = Column("orbit", Text())
    orbit_direction = Column("orbit_direction", Text())
    path = Column("path", Text())
    row = Column("row", Text())
    geometry = Column("geometry", Geometry(geometry_type="POLYGON", srid=4326))
    sensor_mode = Column("sensor_mode", Text())
    product_type = Column("product_type", Text())
    product_info_url = Column("product_info_url", Text())
    product_download_url = Column("product_download_url", Text())
