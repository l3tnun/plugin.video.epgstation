#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import datetime
import simplejson as json
import urllib2
import urlutil
from urlparse import urljoin
from consts import *

addon_handle = int(sys.argv[1])
settings = xbmcaddon.Addon('plugin.video.epgstation')

# dateadded で並び替えできるように設定
xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_DATEADDED)
xbmcplugin.setContent(addon_handle, 'movies')

def addList(video, server_url):
    li = xbmcgui.ListItem(video['name'])

    thumbnail_url = urljoin(server_url, '/thumbnail/' + str(video['id']) + '.jpg')
    li.setIconImage(thumbnail_url)
    li.setArt({
        'poster': thumbnail_url,
        'fanart': thumbnail_url,
        'landscape': thumbnail_url,
        'thumb': thumbnail_url
    })

    startdate = datetime.datetime.fromtimestamp(video['startAt'] / 1000)

    info = {
        'originaltitle': video['name'],
        'title': video['name'],
        'sorttitle': video['name'],
        'tvshowtitle': video['name'],
        'album':  video['name'],
        'year': startdate.strftime('%Y'),
        'date': startdate.strftime('%d.%m.%Y'),
        'aired': startdate.strftime('%Y-%m-%d'),
        'dateadded': startdate.strftime('%Y-%m-%d %H:%M:%S'),
        'duration': (video['endAt'] - video['startAt']) / 1000,
    }

    try:
        # ジャンル
        if 'genre1' in video and video['genre1'] in GENRE1:
            # ジャンル1
            info['genre'] = GENRE1[video['genre1']]

            # ジャンル2
            if 'genre2' in video and video['genre1'] in GENRE2 and video['genre2'] in GENRE2[video['genre1']]:
                info['genre'] += ' / ' + GENRE2[video['genre1']][video['genre2']]

        # 詳細
        if 'description' in video and not 'extended' in video:
            info['plot'] = video['description']
            info['plotoutline'] = video['description']
        elif 'description' in video and 'extended' in video:
            info['plot'] = video['description'] + '\n\n' + video['extended']
            info['plotoutline'] = video['description']
    except:
        print 'error'

    li.setInfo('video', info)

    li.addContextMenuItems([
        ('更新', 'Container.Refresh'),
        ('削除', 'RunScript(%s/delete.py, %d, %s)' % (settings.getAddonInfo('path'), video['id'], video['name']))
    ])

    video_url = urljoin(server_url, '/api/recorded/' + str(video['id']) + '/file')
    if video['original'] == False and 'encoded' in video and len(video['encoded']) > 0:
        video_url += '?encodedId=' + str(video['encoded'][0]['encodedId'])

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=video_url, listitem=li)

if __name__ == '__main__':
    server_url = settings.getSetting('server_url')
    recorded_length = settings.getSetting('recorded_length')

    if not server_url:
        settings.openSettings()
        server_url = settings.getSetting('server_url')

    urlInfo = urlutil.getUrlInfo(server_url)
    request = urllib2.Request(url=urljoin(urlInfo["url"], '/api/recorded?limit=' + str(recorded_length) + '&offset=0'), headers=urlInfo["headers"])
    response = urllib2.urlopen(request)
    strjson = response.read()
    videos = json.loads(strjson)['recorded']

    for video in videos:
        addList(video, server_url)

    xbmcplugin.endOfDirectory(addon_handle)

