import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from greenpt_scrapy.spiders.scrapy_greenpt_spider import ScrapyGreenptSpiderSpider
from scrapy.utils.project import get_project_settings


def execute_spider_single():

    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    process.crawl('scrapy_greenpt_spider')
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':

    execute_spider_single()
