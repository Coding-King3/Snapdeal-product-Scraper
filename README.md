# Snapdeal-product-Scraper
A high-performance Scrapy-based web crawler designed to scrape product details and reviews from Snapdeal.  Unlike basic scrapers, this project implements **"Edge-Case Probing"** to ensure zero data loss during pagination.

# What does this project do? 
This project scrapes data like name, price, URL, Reviewer, Review title and Review Description from any category url that is been sent as argument.
The script saves data in a database using SQLITE in Python. 

# Purpose of making this project? 
I had recently completed my certification of Scrapy on udemy, So creating a project for a eCommerce website helps me to handle challenges as well as it helps us to understand the archiecture of the Scrapy Library. 

# Features
* Made the project dynamic as every category URL on Snapdeal can be scraped.
* Found and used hidden JSON endpoints to scrape data directly.
* Added Random User-Agent to prevent IP blocking.
* Handled pagination for stable and unstable JSON URLs to ensure zero data loss.
* Implemented SQLite logic to save basic data and reviews in separate tables.
* Optimized scraping speed to 15 products per minute using AutoThrottle.

# Tech Used 
 * Language - Python
 * Framework - Scrapy
 * Database - SQLITe

# Getting Started (Installation)
Git Setup 
* Install git on your computer
* Create an empty folder
* Visit that folder, press shift + right click for (Windows) and select gitbash
* Inside git bash paste - "git clone https://github.com/Coding-King3/Snapdeal-product-Scraper.git" without inverted commas

Python setup 
* cd Snapdeal-product-Scraper in your terminal
* Create a virtual environment, type this in terminal python -m venv venv - so now two folders you will see "snapdeal_scrapper_scrapy" and "venv" folder
* For windows - your current folder path /venv/Scripts/activate
* For mac / linux - your current folder venv/bin/activate
* Install scrapy after activating it in same terminal - pip install scrapy
* Now run the scraper in the terminal - scrapy crawl snapdeal_crawler -a category=Cricket -a start_url="https://www.snapdeal.com/products/sports-hobbies-cricket?sort=plrty"
  





  


 
 
 
