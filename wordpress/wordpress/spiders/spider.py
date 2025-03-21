import os
from pathlib import Path
import hashlib

import scrapy
from scrapy.spiders import Rule, CrawlSpider, SitemapSpider
from scrapy.linkextractors import LinkExtractor
from scrapy_playwright.page import PageMethod
import logging
from lxml import etree
import urllib3

logger = logging.getLogger("spider")


def get_domain():
    return os.environ.get("DOMAIN", "wordpress.xxx.xxx.xxx")

# Body Responsive Images
actioneer1 = """
    var element = document.getElementsByTagName("img");
    for (let i = 0; i < element.length; i++) {
        fetch(element[i].src.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.log("No"));
        if (element[i].srcset != "") {
            let images = element[i].srcset.split(',');
            for (let j = 0; j < images.length; j++) {
                let img = images[j].trimLeft().split(" ")[0];
                fetch(img.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
                .catch(() => console.error('oh no!'));
            }
        }
    };
"""

# Body Responsive Picture/Images
actioneer2 = """
    var source = document.getElementsByTagName("source");
    for (let i = 0; i < source.length; i++) {
        if (source[i].srcset != "") {
            let images = source[i].srcset.split(',');
            for (let j = 0; j < images.length; j++) {
                let img = images[j].trimLeft().split(" ")[0];
                fetch(img.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
                .catch(() => console.error('oh no!'));
            }
        }
    }
"""

# Head META-Image
actioneer3 = """
    // msaaplication-TileImage
    let image_msapplication = document.querySelector('meta[name="msapplication-TileImage"]');
    if (null !== image_msapplication) {
        fetch(image_msapplication.content.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
        .catch(() => console.error('oh no!'));
    }

    // og:image
    let image_opengraph = document.querySelector('meta[property="og:image"]');
    if (null !== image_opengraph) {
        fetch(image_opengraph.content.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
        .catch(() => console.error('oh no!'));
    }
"""

# Head LINK-Image/JSON
actioneer4 = """
    const rel_list = ["shortcut icon", "icon", "apple-touch-icon"];
    var headlink = document.getElementsByTagName("link");
    for (let i = 0; i < headlink.length; i++) {
        if (rel_list.includes(headlink[i].rel)) {
            let image = headlink[i].href;
            fetch(image.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
            .catch(() => console.error('oh no!'));
        } else if ("manifest" == headlink[i].rel) {
            // manifest.json
            let jsonfile = headlink[i].href;
            if (0 < jsonfile.length){
                fetch(jsonfile.replace("http://", "https://"))
                .then((resp) => resp.json())
                .then((data) => {
                    for (var icon of data.icons) {
                        if (0 < icon.src.length) {
                            fetch(icon.src.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
                            .catch(() => console.error('oh no!'));
                        }
                    }
                });
            }
        }
    }
"""

# SCHEMA Organization Logo
actioneer5 = """
    var findOrganizationLogo = function(schema) {
        let logo_url = '';
        let schema_items = schema["@graph"];

        for (var item in schema_items) {
            let schema_graph = schema_items[item];
            if("Organization" == schema_graph["@type"]) {
                logo_url = schema_graph["logo"]["contentUrl"];
            }
        }

        return logo_url;
    }

    var script_yoast = document.querySelector('script.yoast-schema-graph');
    let yoast_content = '';
    let yoast_json = '';
    let organization_logo = '';
    if (null !== script_yoast) {
        yoast_content = script_yoast.textContent.trim();
        yoast_json = JSON.parse(yoast_content);
        organization_logo = findOrganizationLogo(yoast_json);

        if (0 < organization_logo.length) {
            fetch(organization_logo.replace("http://", "https://")).then(resp => resp.status === 200 ? console.log("yes") : console.error("No"))
                .catch(() => console.error('oh no!'));
        }
    }
"""

def set_playwright_true(request, response):
    screenshot = os.path.join(Path.cwd(), "output", hashlib.md5(request.url.replace("https://", "").encode()).hexdigest() + ".png")
    request.meta["playwright"] = True
    # request.meta["playwright_include_page"] = True
    request.meta["playwright_page_methods"] = [
        PageMethod("evaluate", actioneer1),
        PageMethod("evaluate", actioneer2),
        PageMethod("evaluate", actioneer3),
        PageMethod("evaluate", actioneer4),
        PageMethod("evaluate", actioneer5),
        #PageMethod("screenshot", path=screenshot, full_page=True),
    ]
    return request


class SpiderSpider(CrawlSpider):
    name = "spider"
    allowed_domains = [get_domain()]
    denied_domains = (
        "api2.branch.io",
        "cdn.taboola.com",
        "connect.facebook.net",
        "utt.impactcdn.com",
        "fonts.gstatic.com",
        "www.google-analytics.com",
        "www.googletagmanager.com",
        "fast.wistia.com",
        "api.dev.xxx.xxx.xxx",
        "api.xxx.xxx.xxx",
        "ssgtm.xxx.xxx.xxx",
        "ka-p.fontawesome.com",
    )

    rules = {
        Rule(LinkExtractor(allow=(""), allow_domains=allowed_domains), follow=True, process_request=set_playwright_true)
    }

    def start_requests(self):
        path = os.path.join(Path.cwd(), "har-output", "log.har")

        # GET request, combined with sitemap links and extra links in request
        # It seems Scrapy cannot crawl the fake 404 page yet -- 26-Jul-24
        sitemaplinks = self.find_all_links()
        extralinks = [f"https://{get_domain()}/404"]
        alllinkts_tocrawl= sitemaplinks + extralinks

        for url in alllinkts_tocrawl:
            # screenshot = os.path.join(Path.cwd(), "output", hashlib.md5(url.replace("https://", "").encode()).hexdigest() + ".png")
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_context_kwargs": {
                    "ignore_https_errors": True,
                    "record_har_content": "attach",
                    "record_har_path": path,
                    "extra_http_headers": {
                        "Accept": "text/html,text/css,*/*;q=0.1",
                        "scrapy": "true"
                    }
                },
                "playwright_page_methods": [
                    PageMethod("evaluate", actioneer1),
                    PageMethod("evaluate", actioneer2),
                    PageMethod("evaluate", actioneer3),
                    PageMethod("evaluate", actioneer4),
                    PageMethod("evaluate", actioneer5),
                    #PageMethod("screenshot", path=screenshot, full_page=True),
                ],
                # "playwright_include_page": True
            })

    async def parse(self, response):
        page = response.meta.get("playwright_page", None)
        logger.info("Parse function called on %s", response.url)
        if page:
            # screenshot = os.path.join(Path.cwd(), "output")
            await page.evaluate(actioneer1)
            await page.evaluate(actioneer2)
            await page.evaluate(actioneer3)
            await page.evaluate(actioneer4)
            await page.evaluate(actioneer5)
            await page.close()
        else:
            logger.error("Failed to get playwright page")

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

    def find_all_links(self, sitemap=f"https://{get_domain()}/wp-sitemap-posts-page-1.xml"):
        xlst = f"https://{get_domain()}/wp-sitemap.xsl"
        data = urllib3.request("GET", sitemap)
        xml_data = data.data.decode() \
            .replace("{http://www.sitemaps.org/schemas/sitemap/0.9}", "") \
            .replace(xlst, "") \
            .replace("http://www.sitemaps.org/schemas/sitemap/0.9", "")
        parser = etree.XMLParser(recover=True)
        xml = etree.fromstring(xml_data.encode(), parser)

        return [x.text for x in xml.xpath('//loc')]
