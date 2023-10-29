#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json


class POISearcher(object):
    def __init__(self, key):
        self.key = key

    def search(self, keywords, **kwargs):
        url = "http://restapi.amap.com/v3/place/text"
        params = {
            "keywords": keywords,
            "key": self.key
        }
        params.update(kwargs)
        self.res = requests.get(url, params)
        if self.res:
            search_result = json.loads(self.res.text)
            return search_result
        else:
            return None
