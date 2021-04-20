import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import GgirobankItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class GgirobankSpider(scrapy.Spider):
	name = 'girobank'
	start_urls = ['http://www.girobank.net/news']

	def parse(self, response):
		articles = response.xpath('//div[@class="girobox_intnav_news"]')
		for article in articles:
			date = article.xpath('.//em/text()').get()
			post_links = article.xpath('.//a[contains(text(),"Read more")]/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

	def parse_post(self, response, date):
		title = response.xpath('(//div[@class="sfContentBlock"]/h2/text())[last()]').get()
		content = response.xpath('//div[@id="T9F092EEE086_Col00"]//text()[not (ancestor::h2)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=GgirobankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
