# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

import scrapy


# def clean_string(value):
#     return value.strip()
#
# def change_rupee(value):
#     if value:
#         replace_text = value.replace(value, '₹' + value)
#         return replace_text
#     return value
#
#
# class SnapdealScrapperScrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#
#     default_output_processor = TakeFirst()
#     url = scrapy.Field(output_processor=TakeFirst())  # Define the new field
#
#     product_name = scrapy.Field(input_processor = MapCompose(clean_string), output_processor = default_output_processor)
#
#     product_price = scrapy.Field(input_processor = MapCompose(change_rupee, clean_string), output_processor = default_output_processor)
#     reviews = scrapy.Field()
#
#

def clean_string(value):
    return value.strip()


class ProductItem(scrapy.Item):
    url = scrapy.Field(output_processor = TakeFirst())
    name = scrapy.Field(
        input_processor = MapCompose(clean_string),
        output_processor = TakeFirst()
    )
    price = scrapy.Field(
        output_processor = TakeFirst()
    )


class ReviewItem(scrapy.Item):
    url = scrapy.Field(output_processor = TakeFirst())
    review_title = scrapy.Field(input_processor = MapCompose(clean_string),
        output_processor = TakeFirst())
    reviewer = scrapy.Field(input_processor = MapCompose(clean_string),
        output_processor = TakeFirst())
    review_description = scrapy.Field(input_processor = MapCompose(clean_string),
        output_processor = TakeFirst())


