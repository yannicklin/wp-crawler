import asyncio
import os
from pathlib import Path
from time import sleep

import scrapy
from playwright.async_api import Page
from scrapy.spiders import Rule, CrawlSpider, Spider
from scrapy.linkextractors import LinkExtractor
from scrapy_playwright.page import PageMethod
import logging

from twisted.internet.asyncioreactor import AsyncioSelectorReactor

logger = logging.getLogger("mycustomlogger")

def set_playwright_true(request, response):
    request.meta["playwright"] = True
    return request

class LegacySpider(CrawlSpider):
    name = "legacy"
    allowed_domains = ["dev.xxx.xxx.xxx"]
    denied_domains = (
        "api.dev.xxx.xxx.xxx",
        "api2.branch.io",
        "www.google-analytics.com",
        "cdn.taboola.com",
        "connect.facebook.net",
        "utt.impactcdn.com",
        "fonts.gstatic.com",
        "www.googletagmanager.com",
        "fast.wistia.com",
        "ssgtm.xxx.xxx.xxx",
    )
    start_urls = ["https://dev.xxx.xxx.xxx"]
    timeout = 60
    rules = {
        Rule(LinkExtractor(deny=[
            "/api.*", "/authorize.*", "/account/.*", "/microui/.*"],
            allow_domains=allowed_domains,
            deny_domains=denied_domains),
            follow=True,
            process_request=set_playwright_true,
            callback="parse",
            errback="errback")
    }

    def __init__(self, *args, **kwargs):
        self.timeout = int(kwargs.pop("timeout", "60"))
        super(LegacySpider, self).__init__(*args, **kwargs)

    def start_requests(self):
       # AsyncioSelectorReactor.callLater(self.timeout, self.stop)
        path = os.path.join(Path.cwd(), "har-output", "log.har")
        screenshot = os.path.join(Path.cwd(), "output", "screenshot.jpg")
        # GET request
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    "ignore_https_errors": True,
                    "record_har_content": "attach",
                    "record_har_path": path,
                    "screen": {
                        "width": 1920,
                        "height": 41000
                    }
                },
                "playwright_page_methods": [
                    #PageMethod('wait_for_selector', 'img', timeout=60000),
                    PageMethod("evaluate", "for(i = 0; i < document.body.scrollHeight; i = i + 10) { window.scroll({top: i, behavior: 'smooth'}); }; new Promise(r => setTimeout(r, 10000));"),
                    PageMethod("screenshot", path=screenshot, full_page=True),
                ],
                "playwright_include_page": False
            })

    async def parse(self, response):
        page = response.meta.get("playwright_page", None)
        logger.info("Parse function called on %s", response.url)
        #await asyncio.sleep(10)
        if page:
            screenshot = os.path.join(Path.cwd(), "output", "example.png")
            content = await page.content()
            #next_page_available = await page.evaluate("""
            #
            #""")
            #await page.screenshot(path=", full_page=True)
            #sleep(10000)
            await page.close()

    async def errback(self, failure):
        logger.info("Failure detected")
        page = failure.meta.get("playwright_page", None)
        if page:
            await page.close()

    async def errback_close_page(self, failure):
        logger.info("Detected failure")
        page = failure.meta.get("playwright_page", None)
        if page:
            await page.close()
