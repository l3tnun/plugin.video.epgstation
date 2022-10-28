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

_url = sys.argv[0]
_handle = int(sys.argv[1])

settings = xbmcaddon.Addon('plugin.video.epgstation')

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urllib.parse.urlencode(kwargs))

def get_categories():
    return VIDEOS

def get_categoryname(category):
    names = [x['searchOption']['keyword'] for x in rules if x['id'] == category]
    return names[0] if len(names) else u'ルールなし'

def get_videos(category):
    return VIDEOS.get(category)

def list_categories():
    xbmcplugin.setPluginCategory(_handle, 'Recorded by epgstation')
    xbmcplugin.setContent(_handle, 'videos')
    categories = get_categories()
    for category in categories:
        category_name = get_categoryname(category)
        list_item = xbmcgui.ListItem(label=category_name)
        list_item.setArt({'thumb': VIDEOS[category][0]['thumb'],
                          'icon': VIDEOS[category][0]['thumb'],
                          'fanart': VIDEOS[category][0]['thumb'],
                          'landscape': VIDEOS[category][0]['thumb']})

        list_item.setInfo('video', {'title': category_name,
                                    'genre': category_name,
                                    'mediatype': 'video'})
        url = get_url(action='listing', category=category)
        is_folder = True
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(_handle)

def list_videos(category):
    xbmcplugin.setPluginCategory(_handle, get_categoryname(category))
    xbmcplugin.setContent(_handle, 'videos')
    videos = get_videos(category)

    if videos is None:
        list_categories()
        return

    for video in videos:
        list_item = xbmcgui.ListItem(label=video['name'])

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
            'mediatype': 'video',
            'plot': video['description'] + '\n\n' + video['extended'],
            'plotoutline': video['description']
        }
        if video.get('genre1') in GENRE1:
            info['genre'] = GENRE1[video['genre1']]

            if video.get('genre1') in GENRE2 and video.get('genre2') in GENRE2[video['genre1']]:
                info['genre'] += ' / ' + GENRE2[video['genre1']][video['genre2']]

        list_item.setInfo('video', info)

        list_item.setArt({'thumb': video['thumb'],
                          'icon': video['thumb'],
                          'fanart': video['thumb'],
                          'landscape': video['thumb']})

        list_item.setProperty('IsPlayable', 'true')

        # コメントは日本語だけと、メニューを英語にしてみたww
        list_item.addContextMenuItems([
            ('Update', 'Container.Refresh'),
            ('Delete', 'RunScript(%s/delete.py, %d, %s)' % (settings.getAddonInfo('path'), video['id'], video['name']))
        ])

        url = get_url(action='play', video=video['video'])
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_DATEADDED)
    xbmcplugin.endOfDirectory(_handle)

def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            list_videos(int(params['category']))
        elif params['action'] == 'play':
            play_video(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_categories()

if __name__ == '__main__':
    server_url = settings.getSetting('server_url')
    recorded_length = settings.getSetting('recorded_length')

    if not server_url:
        settings.openSettings()
        server_url = settings.getSetting('server_url')

    urlInfo = urlutil.getUrlInfo(server_url)

    # 録画済み情報を取得
    apiParam = 'api/recorded?isHalfWidth=true&limit=' + str(recorded_length) + '&offset=0'
    videoRequest = urllib.request.Request(url=urljoin(urlInfo["url"], apiParam), headers=urlInfo["headers"])
    videoResponse = urllib.request.urlopen(videoRequest)
    videoStrjson = videoResponse.read()
    videos = json.loads(videoStrjson)['records']

    # 録画中情報を取得(追っかけ再生用)
    apiParam = 'api/recording?isHalfWidth=true&limit=' + str(recorded_length) + '&offset=0'
    recordingRequest = urllib.request.Request(url=urljoin(urlInfo["url"], apiParam), headers=urlInfo["headers"])
    recordingResponse = urllib.request.urlopen(recordingRequest)
    recordingStrjson = recordingResponse.read()
    recordings = json.loads(recordingStrjson)['records']

    # 録画済みと録画中をマージ
    videos += recordings

    # ルール情報を取得
    ruleRequest = urllib.request.Request(url=urljoin(urlInfo["url"], 'api/rules?limit=0'), headers=urlInfo["headers"])
    ruleResponse = urllib.request.urlopen(ruleRequest)
    ruleStrjson = ruleResponse.read()
    rules = json.loads(ruleStrjson)['rules']

    VIDEOS={}
    for video in videos:
        # フォルダ分けにルール名を使用するため、ルールの名称を取得
        rulenames = [x['searchOption']['keyword'] for x in rules if x['id'] == video.get('ruleId')]
        rulename = rulenames[0] if len(rulenames) else u'ルールなし'
        
        thumbnail_url = urljoin(server_url, 'api/thumbnails/' + str(video['thumbnails'][0])) if len(video['thumbnails']) else ''
        video_url = urljoin(server_url, 'api/videos/' + str(video['videoFiles'][0]['id']))

        # ルールID別にデータを格納。新規ルールはIDが1から振られるようなので、ルールなしは「0」としている
        VIDEOS.setdefault(video.get('ruleId', 0), []).append({
             'id': video['id'],
             'name': video['name'],
             'thumb': thumbnail_url,
             'rulename': rulename,
             'video': video_url,
             'startAt': video['startAt'],
             'endAt': video['endAt'],
             'genre1': video.get('genre1'),
             'genre2': video.get('genre2'),
             'description': video.get('description',''),
             'extended': video.get('extended','')})

    router(sys.argv[2][1:])

