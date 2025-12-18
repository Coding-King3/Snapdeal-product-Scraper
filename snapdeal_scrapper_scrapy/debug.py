import os

# 1. Scrapy command: "-m scrapy crawl [spider_name] -L [log_level]"
# Yehi woh command hai jo PyCharm chala nahi paa raha tha
# NOTE: Apne spider ka naam 'snapdeal_crawler' check kar lena
SCRAPY_COMMAND = "scrapy crawl snapdeal_crawler -L DEBUG"

print(f"Executing command: {SCRAPY_COMMAND}")

# 2. Command ko chalao
# os.system() command ko seedhe operating system terminal mein chalaata hai
os.system(SCRAPY_COMMAND)