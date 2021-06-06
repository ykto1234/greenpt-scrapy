# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy

import excel
import datetime


class GreenptScrapyPipeline(object):
    output_list = []
    index = 1

    def __init__(self, collection_name):
        dt_now = datetime.datetime.now()
        day_str = dt_now.strftime('%Y-%m-%d')
        now_str = dt_now.strftime('%Y-%m-%d_%H%M%S')
        self.filename = '出力結果_' + now_str + '.xlsx'
        self.dirname = day_str
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            collection_name='version'
        )

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        # クローズ時に余っている分を出力
        excel.out_to_excel(self.output_list, self.filename,
                           self.dirname, '出力結果' + str(self.index))

    def process_item(self, item, spider):
        self.output_list.append(item)

        if len(self.output_list) >= 5000:
            excel.out_to_excel(self.output_list, self.filename,
                               self.dirname, '出力結果' + str(self.index))
            self.output_list = []
            self.index += 1

        return item
