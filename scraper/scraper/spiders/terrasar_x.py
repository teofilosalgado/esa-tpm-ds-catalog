from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scraper.items import Product
from scraper.loaders import ProductLoader


class TerraSARXSpider(CrawlSpider):
    name = "TerraSAR-X"
    allowed_domains = ["tpm-ds.eo.esa.int"]
    start_urls = ["https://tpm-ds.eo.esa.int/smcat/TerraSAR-X/"]
    rules = (
        Rule(
            LinkExtractor(
                allow=(r"/smcat/TerraSAR-X/\d+/\w+/\w+/(\d+/)*",),
                deny=(r".*\.txt",),
                attrs=("href", "xlink:href"),
            ),
            follow=True,
        ),
        Rule(
            LinkExtractor(
                allow=(r"/smcat/TerraSAR-X/[a-zA-Z]+/\w+/\w+/.+",),
                deny=(r".*\.txt",),
                attrs=("href",),
            ),
            follow=False,
            callback="parse_item",
        ),
    )

    def _build_xpath(self, category: str):
        return (
            f"//div[@class='field-name'"
            f" and "
            f"text()='{category}']"
            f"/parent::td/following-sibling::td/text()"
        )

    def parse_item(self, response: Response):
        product_download_url = response.xpath(
            "//a[text()='Download Product']/@href"
        ).get()
        tables = response.xpath("//table")
        for table in tables:
            product = ProductLoader(item=Product(), selector=table)
            product.add_xpath("acquisition_date", self._build_xpath("Acquisition Date"))
            product.add_xpath("stop_date", self._build_xpath("Stop Date"))
            product.add_xpath("orbit", self._build_xpath("Orbit"))
            product.add_xpath("orbit_direction", self._build_xpath("Orbit Direction"))
            product.add_xpath("path", self._build_xpath("Path"))
            product.add_xpath("row", self._build_xpath("Row"))
            product.add_xpath("geometry", self._build_xpath("Geographical Coverage"))
            product.add_xpath("sensor_mode", self._build_xpath("Sensor Mode"))
            product.add_xpath("product_type", self._build_xpath("Product Type"))
            product.add_value("product_info_url", response.url)
            product.add_value("product_download_url", product_download_url)
            yield product.load_item()
