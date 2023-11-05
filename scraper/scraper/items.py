# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class Product(Item):
    acquisition_date = Field()
    stop_date = Field()
    orbit = Field()
    orbit_direction = Field()
    path = Field()
    row = Field()
    geometry = Field()
    sensor_mode = Field()
    product_type = Field()
    product_info_url = Field()
    product_download_url = Field()
