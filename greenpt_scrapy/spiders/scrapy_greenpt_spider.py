import logging
import scrapy
from bs4 import BeautifulSoup
from greenpt_scrapy.items import GreenptScrapyItem
import excel

# ログの定義
import mylogger
import urllib
import datetime
import os
logger = mylogger.setup_logger(__name__)
logger.info('プログラム起動開始')


class CategoryInfo:
    def __init__(self):
        self.id = None
        self.category_title = None


class ScrapyGreenptSpiderSpider(scrapy.Spider):
    name = 'scrapy_greenpt_spider'
    allowed_domains = ['goods.greenpt.mlit.go.jp']
    url = 'https://goods.greenpt.mlit.go.jp/apl/public/viewShouhinList'
    # カテゴリのIDとタイトルのリスト
    category_list = []
    output_list = []
    index = 1

    def __init__(self, *args, **kwargs):
        super(ScrapyGreenptSpiderSpider, self).__init__(*args, **kwargs)
        dt_now = datetime.datetime.now()
        day_str = dt_now.strftime('%Y-%m-%d')
        now_str = dt_now.strftime('%Y-%m-%d_%H%M%S')
        self.filename = '出力結果_' + now_str + '.xlsx'
        self.dirname = day_str

    def start_requests(self):
        logger.info('スクレイピング開始')
        logger.info(self.url)
        yield scrapy.Request(self.url, callback=self.category_list_parse)

    def category_list_parse(self, response):
        """
        カテゴリの一覧からカテゴリのIDとタイトルを取得する
        """
        try:
            category_container_sel = 'div.product-search-filter-category__row'
            category_radio_sel = 'div.c-form-radio'
            _soup = BeautifulSoup(response.text, 'html.parser')
            category_container_eles = _soup.select(category_container_sel)
            if len(category_container_eles):
                category_radio_eles = category_container_eles[0].select(
                    category_radio_sel)

            for category_ele in category_radio_eles:
                _category_info = CategoryInfo()
                # カテゴリID取得
                category_input_ele = category_ele.select(
                    "input[name='category']")
                if len(category_input_ele):
                    category_id = category_input_ele[0].get('value')

                # カテゴリ名取得
                category_title_ele = category_ele.select('span')
                if len(category_title_ele):
                    category_title = category_title_ele[0].text

                if category_id and category_title:
                    _category_info.id = category_id
                    _category_info.category_title = category_title
                    self.category_list.append(_category_info)

                if category_title == None:
                    pass

            for category_info in self.category_list:
                item_list_url = self.url + \
                    '?otherItem=&keyword=&prefId=&theme=&pointH=&pointRadioId=&outTerm=&noStock=&subId=' + category_info.id
                request = scrapy.Request(
                    item_list_url, callback=self.item_list_parse)
                yield request

            return

        except:
            import traceback
            logger.error('エラーが発生しました')
            traceback.print_exc()
            err_message = traceback.format_exc()
            logger.error(err_message)

    def item_list_parse(self, response):

        try:
            item_container_sel = 'div.product-lv2-list__item.product-lv2-item'
            item_name_sel = 'div.product-lv2-item__name > span'
            item_tag_sel = 'li.product-lv2-item__tag-label'
            item_point_sel = 'div.product-lv2-item__number'
            item_company_sel = 'div.product-lv2-item__business'
            next_page_sel = 'a.pager__btn-next'
            disable_next_page_sel = 'a.pager__btn-next.pager__btn--disabled'

            qs = urllib.parse.urlparse(response.url).query
            qs_d = urllib.parse.parse_qs(qs)
            target_id = qs_d['subId'][0]
            target_category_list = [
                i for i in self.category_list if i.id == target_id]
            category_name = target_category_list[0].category_title

            _soup = BeautifulSoup(response.text, 'html.parser')
            item_container_eles = _soup.select(item_container_sel)

            for item_container_ele in item_container_eles:
                item_name_ele = item_container_ele.select(item_name_sel)
                item_tag_ele = item_container_ele.select(item_tag_sel)
                item_point_ele = item_container_ele.select(item_point_sel)
                item_company_ele = item_container_ele.select(item_company_sel)

                item = GreenptScrapyItem()
                item['item_category'] = category_name
                item['item_name'] = item_name_ele[0].text
                item['item_tag'] = item_tag_ele[0].text
                item['item_point'] = item_point_ele[0].text
                item['company'] = item_company_ele[0].text
                yield self.output_excel(item)

            next_page_eles = _soup.select(next_page_sel)
            disable_next_page_eles = _soup.select(disable_next_page_sel)
            if len(disable_next_page_eles):
                # 次のページボタンが非活性の場合
                return

            if len(next_page_eles):
                # 次のページがある場合
                if 'page' in qs_d:
                    page_num = int(qs_d['page'][0])
                    page_num += 1
                else:
                    page_num = 1

                yield scrapy.Request(
                    self.url + '?otherItem=&keyword=&prefId=&theme=&pointH=&pointRadioId=&outTerm=&noStock=&subId=' +
                    target_id + '&page=' + str(page_num),
                    callback=self.item_list_parse)

        except:
            import traceback
            logger.error('エラーが発生しました')
            traceback.print_exc()
            err_message = traceback.format_exc()
            logger.error(err_message)

    def output_excel(self, item):
        self.output_list.append(item)

        if len(self.output_list) >= 10000:
            excel.out_to_excel(self.output_list, self.filename,
                               self.dirname, '出力結果' + str(self.index))
            logger.info('出力結果' + str(self.index) + 'を出力しました。')
            self.output_list = []
            self.index += 1

        return item

    def closed(self, reason):
        # クローズ時に余っている分を出力
        excel.out_to_excel(self.output_list, self.filename,
                           self.dirname, '出力結果' + str(self.index))
        logger.info('スクレイピング処理完了')
        print('----------------------------------------------------')
        print('          スクレイピング処理が完了しました')
        print('----------------------------------------------------')
        # 『続行するには何かキーを押してください . . .』と表示させる
        os.system('PAUSE')
