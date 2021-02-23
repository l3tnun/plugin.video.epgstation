#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon
import os
import sys
import urllib.request, urllib.error, urllib.parse
import urlutil
from urllib.parse import urljoin

settings = xbmcaddon.Addon('plugin.video.epgstation')
plugin = settings.getAddonInfo('name')

if __name__ == '__main__' and len(sys.argv) == 3:
    server_url = settings.getSetting('server_url')
    videoId = sys.argv[1];
    fileName = sys.argv[2];
    opener = urllib.request.build_opener(urllib.request.HTTPHandler)

    dialog = xbmcgui.Dialog()
    if dialog.yesno(xbmc.getLocalizedString(122).encode('utf_8'), fileName + 'を削除しますか?', yeslabel=xbmc.getLocalizedString(117)):
        progress = xbmcgui.DialogProgress()
        progress.create(plugin, '削除中...')
        progress.update(0)

        try:
            urlInfo = urlutil.getUrlInfo(server_url)
            req = urllib.request.Request(url=urljoin(urlInfo["url"], 'api/recorded/' + str(videoId)), headers=urlInfo["headers"])
            req.get_method = lambda: 'DELETE'
            url = opener.open(req)
        except:
            xbmc.log('削除に失敗しました: %s' % videoId, level=xbmc.LOGERROR)
            progress.close()
            xbmcgui.Dialog().ok(xbmc.getLocalizedString(16205), xbmc.getLocalizedString(16206))
            sys.exit(1)

        xbmc.sleep(200)
        progress.update(100)
        progress.close()

        # 選択位置を一つ上に移動する
        xbmc.sleep(500)
        xbmc.executebuiltin('Action(Up)')

        # リスト更新
        xbmc.executebuiltin('Container.Refresh')


    sys.exit(0)

