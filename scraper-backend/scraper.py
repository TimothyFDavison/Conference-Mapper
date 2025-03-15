import scrapy
import scrapy.crawler as crawler
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Queue
from twisted.internet import reactor

import config

class WikiCFPSpider(scrapy.Spider):
    name = config.SCRAPER_NAME
    allowed_domains = [config.SCRAPER_DOMAIN]

    def __init__(self, subpage=None, *args, **kwargs):
        super(WikiCFPSpider, self).__init__(*args, **kwargs)
        self.page_count = 0
        self.page_maximum = config.PAGE_COUNT_MAXIMUM
        if subpage:
            self.start_urls = [config.START_URL.format(subpage)]
            self.subpage = subpage.replace(" ", "_")
        else:
            self.start_urls = []

    def parse(self, response):
        """
        Grabs the table from a WikiCFPSpider page, iterates over the rows
        """
        # Find table on page
        table = response.xpath('//div[@class="contsec"]//table[@cellpadding="3" and @cellspacing="1"]')

        # Retrieve and iterate over rows
        rows = table.xpath('.//tr[position() > 1]')
        for row in rows:
            cells = row.xpath('.//td')
            row_data = [cell.xpath('string(.)').get().strip() for cell in cells]
            yield {'data': "||||".join(row_data)}

        # Check for "next" button and follow it if it's there, up to 5 times
        if self.page_count < self.page_maximum:
            next_page = response.xpath('//a[contains(text(), "next")]/@href').get()
            if next_page:
                self.page_count += 1
                yield response.follow(next_page, callback=self.parse)


def run_spider(spider, subpage):
    """
    Wrapper to run the spider in separate processes, to avoid issues with twisted.reactor.
    """

    def f(q):
        try:
            # Set pipeline to output into postgres
            settings = get_project_settings()
            settings.set("ITEM_PIPELINES", {
               'scraper_pipelines.pipelines.PostgreSQLPipeline': 100
            }, priority='spider')

            # Execute the runner over the given domain
            runner = crawler.CrawlerRunner(settings)
            deferred = runner.crawl(spider, subpage=subpage)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    # Execute in subprocess
    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result
    """
    settings = get_project_settings()
    settings.set("ITEM_PIPELINES", {
        'scraper_pipelines.pipelines.PostgreSQLPipeline': 100
    }, priority='spider')
    process = crawler.CrawlerProcess(settings)
    process.crawl(spider, subpage=subpage)
    process.start()
    """
