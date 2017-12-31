#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui, xbmcaddon
import os
import sys
import urllib2
from urlparse import urljoin

settings = xbmcaddon.Addon('plugin.video.epgstation')
plugin = settings.getAddonInfo('name')

if __name__ == '__main__' and len(sys.argv) == 3:
    server_url = settings.getSetting('server_url')
    videoId = sys.argv[1];
    fileName = sys.argv[2];
    opener = urllib2.build_opener(urllib2.HTTPHandler)

    dialog = xbmcgui.Dialog()
    if dialog.yesno(xbmc.getLocalizedString(122).encode('utf_8'), xbmc.getLocalizedString(433).encode('utf_8') % fileName, yeslabel=xbmc.getLocalizedString(117)):
        progress = xbmcgui.DialogProgress()
        progress.create(plugin, '削除中...')
        progress.update(0)

        try:
            req = urllib2.Request(urljoin(server_url, '/api/recorded/' + str(videoId)))
            req.get_method = lambda: 'DELETE'
            url = opener.open(req)
        except:
            xbmc.log('削除に失敗しました: %s' % videoId, level=xbmc.LOGERROR)
            progress.close()
            xbmcgui.Dialog().ok(xbmc.getLocalizedString(16205), xbmc.getLocalizedString(16206))
            sys.exit(1)

        xbmc.executebuiltin('Container.Refresh') # list 更新

        xbmc.sleep(400)
        progress.update(100)

    sys.exit(0)

