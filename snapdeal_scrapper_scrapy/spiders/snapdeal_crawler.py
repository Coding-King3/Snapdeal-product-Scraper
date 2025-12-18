import os
from snapdeal_scrapper_scrapy.items import ProductItem, ReviewItem
import scrapy
from scrapy.loader import ItemLoader
import math


class SnapdealCrawlerSpider(scrapy.Spider):
    name = "snapdeal_crawler"
    allowed_domains = ["www.snapdeal.com"]
    # The page count given here, is the limit of the links that are available on the api page

    page_count = 20

    def __init__(self, *args, **kwargs):

        super(SnapdealCrawlerSpider, self).__init__(*args, **kwargs)
        category_arg = kwargs.get('category')
        url_val = kwargs.get('start_url')

        # The above code sets url as well category name while entering it in terminal using -a command
        # The category is added so that the database names has category in it,
        # The url_val is the url sent to the spider for visiting the landing page.

        self.seen_urls = set()

        if url_val:
            self.start_urls = [url_val]
        else:
            raise ValueError("You must provide a url in command line using -a start_url=")

        if category_arg:
            self.category_name = category_arg
        else:
            self.category_name = os.environ.get('CATEGORY_NAME', 'default_category')

        self.category_name = self.category_name.lower().replace(' ', '_')
        self.logger.info(f"Scraping category: {self.category_name} to database: snapdeal_data_{self.category_name}.db")



    def parse(self, response):
        initial_offset = 0
        # Initial offset is kept at 0 for fist, but it will increment it's value by 20 everytime,
        # till it reaches its last page of finding the product urls.

        # The cat val basically scrapes category value from the backend of the parsed HTML PAGE,
        # This cat values will dynamic generate the json url from the given below format in url variable

        cat_val = response.css("[id = 'labelId']::attr(value)").get()
        if cat_val:
            url = f"https://www.snapdeal.com/acors/json/product/get/search/{cat_val}/{initial_offset}/{self.page_count}"


            # Sending request to the above url variable, calling self.parse_product_page method
            # Meta is a datapacket (meta keys) it stays with scrapy and it can be accessed on passed method
            # It can be accessed via response.meta.get(key name) in any passed method


            yield scrapy.Request(
                url = url,
                callback=self.parse_product_page,
                meta = {'offset' : initial_offset, 'cat_id' : cat_val}

            )

    def parse_product_page(self, response):
        # The product links fetches all the a href tags available in the json url followed by cat id, offset and pagecount
        
        product_links = response.css("[class = 'product-tuple-image '] a::attr(href)").getall()

        # Below low visits each url and callbacks parse_product_details which scrapes
        # basic data, name, price, url etc
        for link in product_links:
            yield scrapy.Request(url = link,
                                 callback=self.parse_product_details)

        # The below lines fetches / updates the below provided  value
        # and then again sends request to new generated url with updated values

        current_offset = response.meta.get('offset')
        cat_id = response.meta.get('cat_id')
        next_offset = current_offset + self.page_count

        # Below condition checks whether products are available in the link,
        # if yes, then it will send request to the url and again call parse_product_page,
        # where it will run a loop and call parse_product_details for scraping purpose,
        # some sort of recursion

        if product_links:
            next_url =  f"https://www.snapdeal.com/acors/json/product/get/search/{cat_id}/{next_offset}/{self.page_count}"
            yield scrapy.Request(
                url = next_url,
                callback=self.parse_product_page,
                meta = {'offset' : next_offset, 'cat_id' : cat_id}
            )
        else:

            # The else part logic,
            # Now while testing the script with different scenarios,
            # The json url has a format, cat_id/next_offset/self.page_count - it's default by 20
            # Now in soem scenarios, in a url if only 14 prodcuts are available and we give 20 page_count value
            # It may work and give us all 14 urls, but this feature is not working for all urls.

            # for some urls if we give cat_id/800/20, it will return 0, wheras rather than 20 we give 14
            # it will work properly,

            # so for this reason we have created a else block which will handle the scenario properly.
            # For dealing with this I have created a link_check method where it handles the duplicates
            # and send the scrapy_request to parse_product_details which if condition was doing.

            # If we haven't created this logic and assume if there are 884 urls
            # the scrapy with it's default parameter would scrape only 880 urs and rest 4 will not be scraped

            # But with below logic this works properly.

            # dont_filter = True has added in scrapy_request so that scrapy doens't consdier the url as duplicate and
            # allows the scraping

            self.logger.info(
                f"EMPTY BATCH DETECTED: cat_id={cat_id}, offset={current_offset}, limit={self.page_count}. Starting PROBE...")
            for b in range(1, 20 + 1):
                probe_url = f"https://www.snapdeal.com/acors/json/product/get/search/{cat_id}/{current_offset}/{b}"
                yield scrapy.Request(
                    url=probe_url,
                    callback=self.link_check,
                    meta={'cat_id': cat_id, 'offset': current_offset},
                    dont_filter=True)

    def link_check(self, response):

        # Problinks var checks if product links are available or not
        probe_links = response.css("[class = 'product-tuple-image '] a::attr(href)").getall()

        # If available it will run a loop as getall() converts the data into list
        # and will check whether in self.seen_urls current url is present or not
        # If not only then it will add the url in the set and will sent to scrapy request,

        # The reason for creating the set is, probe links is using getall()
        # so if 14 urls are there, it will check it one by one,
        # technically, using a set only unique url would be added,
        # and if link is not present in the set() only then it would be allowed to send a request
        # This way we would not process multiple duplicate request and we will get n of required data


        if probe_links:
            for link in probe_links:
                # Check karo ki kya ye link hum pehle hi scrape kar chuke hain?
                if link not in self.seen_urls:
                    self.seen_urls.add(link)
                    self.logger.info(f"Found missing product during probe: {link}")
                    yield scrapy.Request(
                        url=link,
                        callback=self.parse_product_details
                    )

    def parse_product_details(self, response):

        # This method creates a loader from Itemloader class, which creates item of ProductItem() class
        # in items .py,

        loader = ItemLoader(item = ProductItem(), response = response)

        # Below are way to retrieve data using css / xpath whatever you prefer

        loader.add_css("name", "[class = 'col-xs-22'] h1::attr(title)")
        loader.add_css("price", "[class = 'payBlkBig']::text")
        loader.add_value("url", response.url)


        # The item varialble here applies data processing / conditions you've mentioned in
        # items.py and then it's ready for yield purpose
        item = loader.load_item()

        yield item
        # yield item sends data out of the spider towards scrapy Enginer (pipelines.py)

        review_url = response.url + "/reviews?"

        yield scrapy.Request(
            url = review_url,
            meta = {'product_item' : item},
            callback=self.parse_reviews
        )


    def parse_reviews(self, response):

        # The parse_reviews method is use to get the basic details from the page
        # and send request to a method which will scrape the review



        item1 = response.meta.get('product_item')
        total_number_of_reviews = 10
        extract_count_from_review = response.css("[class = 'total LTgray reviewCount']::text").get()
        if extract_count_from_review:
            get_count_of_reviews = int(extract_count_from_review.split()[2])
            total_number_of_pages_to_visit = math.ceil(get_count_of_reviews / total_number_of_reviews)

        # The above lines actually Retreive total number of review available from and html text
        # once found the number it uses math.ceil to round of the number which we get after dividing it with 10
        # why ten, maximum number of reviews per page
        # example if 64 reviews are available on the product page,
        # For 60 pages it would do 6 review page request, but as 4 pages would be remaining
        # math.ceil will do it 7 -- 64 / 10 = 6.4 math.ceil (7)


            # Below code actually scrapes data from the first page,
            # as if count of reviews be 1 or 10, in landing page, data of first page review will
            # be there, so it better to not send a another request for same thing that is
            # available on the landing page itself
            response.meta['page_no'] = 1
            response.meta['product_item'] = item1
            for review in self.scrape_reviews(response):
                yield review

            # Below code works for pages where count is greater than 1
            # it will visit url +?page=2 and till it s length and
            # call scrape_reviews method which will extract all reviews from the mentioned page.

            if total_number_of_pages_to_visit > 1:
                for page_no in range(2, total_number_of_pages_to_visit + 1):
                    next_page_url = response.url + f'?page={page_no}'

                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.scrape_reviews,
                        meta={'product_item': item1, 'page_no': page_no}
                    )

        else:

            # Below code is where no reviews are there,
            # We have added a condition where if nothing is found, we would mark it as not there

            response.meta['page_no'] = 1
            response.meta['product_item'] = item1
            for review in self.scrape_reviews(response):
                yield review


    def scrape_reviews(self, response):
        # base_product_data = response.meta.get('product_item')

        # Below element finds all the elements which has data of the review

        main_review_element = response.css("[id = 'defaultReviewsCard'] [class = 'user-review']")

        # Below code check if reviews are available, if yes, then try to fetch data
        # else raise exception in the logger
        # Here in scrape_review method we have created an Item of ReviewItem() class from items.py

        if main_review_element:
            for b in main_review_element:
                try:
                    review_item = ReviewItem()
                    # review_item['url'] = base_product_data.get('url', response.url).strip()
                    review_item['url'] = response.url.strip()
                    review_item['review_title'] = (b.css("[class = 'head']::text").get() or "").strip()
                    review_item['reviewer'] = (b.css("[class = '_reviewUserName']::attr(title)").get() or "").strip()
                    review_item['review_description'] = (b.css("p::text").get() or "").strip()

                    yield review_item

                except AttributeError as e:
                    self.logger.warning(f"Attribute error while parsing url {response.url}")
                    continue
        else:
            # Below code will send not there where no review is found.


            review_item = ReviewItem()
            # review_item['url'] = base_product_data.get('url', response.url).strip()
            review_item['url'] = response.url.strip()
            review_item['review_title'] = review_item['reviewer'] = review_item['review_description'] = 'Not There'
            yield review_item


