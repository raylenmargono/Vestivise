import urllib2
import requests
from lxml import html, etree
import re
import json

class _HoldingsAutoCompleter:

    def get_element(self, tree, xpath):
        result = self.get_elements(tree, xpath)
        if result:
            return result[0]
        return None

    def get_elements(self, tree, xpath):
        if tree is None: return None
        return tree.xpath(xpath)

    def get(self, url, params=None):
        return html.fromstring(requests.get(url, params=params).content)

    def browse(self, element):
        html.open_in_browser(element)

    def run(self, secname):
        tree = self.get("https://www.google.com/search", params={
            "q" : secname + " morningstar"
        })
        morning_star_potential = self.get_elements(tree, "//a[.//*[contains(text(), 'Morningstar')] or contains(text(), 'Morningstar')]")
        for m in morning_star_potential:
            link = self.get_element(m, "@href")
            clean_link = urllib2.unquote(re.search("\/url\?q=(.+)", link).group(1))
            info_page = self.get(clean_link)
            content = etree.tostring(info_page)
            json_match = re.search("Security = (.*?})", content)
            if json_match:
                payload = json.loads(json_match.group(1))
                secname = payload.get("securityName")
                isin = payload.get("ISIN")
                ticker = payload.get("ticker")

#HoldingsAutoCompleter = _HoldingsAutoCompleter()