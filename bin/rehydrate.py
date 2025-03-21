import argparse
import json
import os.path
import re
import urllib
from os import makedirs
from os.path import join, dirname

import logging
import sys
from typing import Generator
from urllib.parse import urlparse, unquote

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout)] # TODO: We can't use stderr as ADO uses that to determine if the task was a failure...
)

logger = logging.getLogger('rehydrate')

def _get_args():
    ########## Arg Parser ########
    parser = argparse.ArgumentParser()
    parser.add_argument("har_dir")
    parser.add_argument("--output", dest="output", required=False, default="../output",
                        help="The output directory to put the site")
    parser.add_argument("--is-localhost", dest="is_localhost", required=False, default=None,
                        help="If we are running this from localhost", action="store_true")
    parser.add_argument("--use-domain", dest="use_domain", required=False, default="{{domain}}",
                        help="Specific domain to rename to")
    return parser.parse_args()

def main():
    args = _get_args()
    with open(join(args.har_dir, "log.har"), 'r') as har_f:
        data = json.loads(har_f.read())
        entries = data["log"]["entries"]
        for e in entries:
            rehydrate_file(process_entry(e), args.har_dir, args.output, args.is_localhost, args.use_domain)


def _transform_html_name(html: str):
    return f"{html}index.html"


def process_entry(entry: dict) -> tuple:
    origin = urlparse(entry["request"]["url"])
    if "dev.xxx.xxx.xxx" in origin.netloc or "xxx.xxx.xxx" in origin.netloc:
        concentrate = entry["response"]["content"].get("_file", "NO_FILE")
        if concentrate == "NO_FILE":
            if entry["response"]["status"] in [301, 302]:
                logger.info(f"Found redirect for [{str(origin)}]")
            #else:
            #    logger.info(f"No end file found for [{origin}]....")
        else:
            if entry["response"]["status"] in [404]:
                logger.debug(f"Ignore not found paths [{str(origin.path)}]")
            if entry["response"]["status"] in [500, 501, 502]:
                logger.warning(f"Do not rehydrate failed files [{str(origin.path)}]")
            destination = origin.path
            if "text/html" in entry["response"]["content"]["mimeType"]:
                destination = _transform_html_name(origin.path)
            logger.debug(f"[{concentrate}] -> [{origin}]")
            if entry["response"]["status"] < 400:
                yield (concentrate, destination)


def rehydrate_file(cordial, datadir: str, outputdir: str, is_localhost: bool, domain: str):
    for c in cordial:
        with open(join(datadir, c[0]), 'rb') as r:
            filename = c[1][1:] if c[1][0] == "/" else c[1]
            dir_name = dirname(filename)
            if dir_name != "":
                makedirs(join(outputdir, dir_name), exist_ok=True)
            try:
                file_flavour(filename, outputdir, r, is_localhost, domain=domain)
            except Exception as ex:
                logger.error(ex)
                logger.error(f"Failed to save file: [{filename}]")


def file_flavour(filename: str, outputdir: str, r, local_host = False, cf_image = False, domain = "{{domain}}"):
    if unquote(filename) != filename:
        logger.warning(f"Escaped characters in filename: [{filename}]")
    with open(join(outputdir, unquote(filename)), 'wb+') as w:
        data = r.read()
        if len(data) == 0:
            raise Exception(f"Files are not allowed to be empty [{filename}]")
        if ".html" in filename or ".css" in filename or ".js" in filename:
            content = data.decode()

            replace = content.replace("http://wordpress", "https://wordpress") \
                .replace("https://dev.xxx.xxx.xxx", "") \
                .replace("https://assets.xxx.xxx.xxx", ".") \
                .replace("https://wordpress.dev.xxx.xxx.xxx", f"https://{domain}") \
                .replace("https://wordpress.stg.xxx.xxx.xxx", f"https://{domain}") \
                .replace("https://wordpress.xxx.xxx.xxx", f"https://{domain}") \
                .replace("wordpress.xxx.xxx.xxx", f"{domain}")

            if local_host:
                replace = replace.replace("https://{{domain}}", "")
                replace = replace.replace("=\"/", "=\"/scraper/output/")
                replace = replace.replace(" /static", " /scraper/output/static")
                replace = replace.replace("return\"/static-content", "return\"/scraper/output/static-content")
                #replace = replace.replace("static-content", "scraper/output/static-content")

            if cf_image:
                replace = re.sub(r"(\/static-content\/[\w\/\-\.@]*(\.jpg|\.jpeg|\.png|\.svg|\.gif))", "/cdn-cgi/image/format=auto\\1", replace)

            w.write(replace.encode())

        else:
            w.write(data)


if "__main__" == __name__:
    main()
