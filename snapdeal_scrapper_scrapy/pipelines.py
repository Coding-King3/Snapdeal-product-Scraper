# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
from .items import ProductItem, ReviewItem

# import openpyxl
#
#
# class SnapdealScrapperScrapyPipeline:
#     def __init__(self):
#         self.workbook = openpyxl.Workbook()
#         self.sheet = self.workbook.active
#         self.sheet.title = 'Snapdeal Products'
#         self.headers_written = False
#
#     def process_item(self, item, spider):
#         if not self.headers_written:
#             self.field_names = list(item.keys())
#             self.sheet.append(self.field_names)
#             self.headers_written = True
#
#         row_values = [item.get(field) for field in self.field_names]
#         self.sheet.append(row_values)
#         return item
#
#     def close_spider(self, spider):
#         try:
#             self.workbook.save("snapdeal_output.xlsx")
#         except Exception as e:
#             print(e)
#
#
#

class SQLitePipeline:

    def open_spider(self, spider):
        category = getattr(spider, 'category_name', 'default_category')
        self.db_name = f'snapdeal_data_of_{category}.db'
        self.conn = sqlite3.connect(self.db_name)
        self.cur = self.conn.cursor()
        self.create_tables()


    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()

    def create_tables(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS Products
            (url TEXT PRIMARY KEY, 
            name TEXT, 
            price TEXT)
        """)

        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Reviews
            (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            url TEXT, 
            review_title TEXT, 
            reviewer TEXT, 
            review_description TEXT
            )
            """
        )


    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            self.cur.execute("""
            INSERT OR IGNORE INTO Products 
            (url, name, price) Values (?,?,?)
            """,(
                item.get('url'),
                item.get('name'),
                item.get('price')
            ))
        elif isinstance(item, ReviewItem):
            self.cur.execute(
                """
                INSERT INTO Reviews (url, review_title, reviewer, review_description)
                VALUES (?, ? , ?, ?)
                """,(
                    item.get('url'),
                    item.get('review_title'),
                    item.get('reviewer'),
                    item.get('review_description')
                )
            )


        return item