#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

amap_keys = [
    "6809f51ea24cd02694e4639bb85260ea"
    "f4a7973d38dad930c86b91fb0cbdc09b"
]


class AmapKey(object):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        pass



class AmapGecoder(object):
    def __init__(self, key):
        self.key = key

    def geocode(self, address, city = None, output = "JSON", **kwargs):
        params = {
            "key": self.key,
            "address": address,
            "output": output
        }
        if city:
            params["city"] = city
        params.update(kwargs)
        self.res = requests.get(url = "http://restapi.amap.com/v3/geocode/geo", params = params)
        if self.res:
            return json.loads(self.res.content)
        else:
            return None

