#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
import datetime
import simplejson as json
import urllib.request, urllib.error, urllib.parse
import urlutil
from urllib.parse import urljoin
from consts import *

addon_handle = int(sys.argv[1])
settings = xbmcaddon.Addon('plugin.video.epgstation')

# dateadded で並び替えできるように設定
xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_DATEADDED)
xbmcplugin.setContent(addon_handle, 'movies')

def addList(video, server_url):
    li = xbmcgui.ListItem(video['name'])
    if video['thumbnails']:
        thumbnail_url = urljoin(server_url, 'api/thumbnails/' + str(video['thumbnails'][0]))
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

            # サブジャンル
            if 'subGenre1' in video and video['genre1'] in GENRE2 and video['subGenre1'] in GENRE2[video['genre1']]:
                info['genre'] += ' / ' + GENRE2[video['genre1']][video['subGenre1']]

        # 詳細
        if 'description' in video and not 'extended' in video:
            info['plot'] = video['description']
            info['plotoutline'] = video['description']
        elif 'description' in video and 'extended' in video:
            info['plot'] = video['description'] + '\n\n' + video['extended']
            info['plotoutline'] = video['description']
    except:
        print('error')

    li.setInfo('video', info)

    li.addContextMenuItems([
        ('更新', 'Container.Refresh'),
        ('削除', 'RunScript(%s/delete.py, %d, %s)' % (settings.getAddonInfo('path'), video['id'], video['name']))
    ])

    video_url = urljoin(server_url, 'api/videos/' + str(video['videoFiles'][0]['id']))
    # if video['original'] == False and 'encoded' in video and len(video['encoded']) > 0:
    #     video_url += '?encodedId=' + str(video['encoded'][0]['encodedId'])

    xbmcplugin.addDirectoryItem(handle=addon_handle, url=video_url, listitem=li)

if __name__ == '__main__':
    server_url = settings.getSetting('server_url')
    recorded_length = settings.getSetting('recorded_length')

    if not server_url:
        settings.openSettings()
        server_url = settings.getSetting('server_url')

    urlInfo = urlutil.getUrlInfo(server_url)

    request = urllib.request.Request(url=urljoin(urlInfo["url"], 'api/recorded?isHalfWidth=true&limit=' + str(recorded_length) + '&offset=0'), headers=urlInfo["headers"])
    response = urllib.request.urlopen(request)
    strjson = response.read()
    videos = json.loads(strjson)['records']

    for video in videos:
        addList(video, server_url)

    xbmcplugin.endOfDirectory(addon_handle)

