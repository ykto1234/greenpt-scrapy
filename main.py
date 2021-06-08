import scrapy
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from greenpt_scrapy.spiders.scrapy_greenpt_spider import ScrapyGreenptSpiderSpider
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Queue
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
import logging
import os


def call_spider(queue):
    try:
        configure_logging()
        logging.basicConfig(level=logging.DEBUG)

        runner = CrawlerRunner()
        deferred = runner.crawl(ScrapyGreenptSpiderSpider)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        queue.put(None)
    except Exception as e:
        queue.put(e)


def execute_spider():
    queue = Queue()
    process = Process(target=call_spider, args=(queue, ))
    process.start()
    result = queue.get()
    process.join()


def execute_spider_single():

    settings = get_project_settings()
    process = CrawlerProcess(settings=settings)

    # 'followall' is the name of one of the spiders of the project.
    process.crawl('scrapy_greenpt_spider')
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':

    # pyinstallerでexe化後にscrapyのmultiprocessが上手く動かない問題回避用
    import multiprocessing as mp
    mp.freeze_support()

    # execute_spider_single()
    # 『続行するには何かキーを押してください . . .』と表示させる
    print('----------------------------------------------------')
    print('          スクレイピング処理を開始します。')
    print('  ※中止する場合は、×ボタンで画面を閉じてください。')
    print('----------------------------------------------------')
    os.system('PAUSE')
    execute_spider()
