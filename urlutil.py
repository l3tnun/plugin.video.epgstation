#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

# urllib2.Request で開く url と headers を生成する
def getUrlInfo(server_url):
    result = {
        "url": None,
        "headers": {}
    }
    match = re.search(r"^(http|https)://(.+):(.+)@(.+)", server_url)

    if match is not None:
        # BASIC 認証
        result["url"] = match.group(1) + "://" + match.group(4);
        result["headers"]["authorization"] = "Basic " + (match.group(2) + ":" + match.group(3)).encode("base64")[:-1]
    else:
        match = re.search(r"^(http|https)://(.+)", server_url)
        result["url"] = match.group(1) + "://" + match.group(2);

    return result

