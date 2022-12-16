import xbmc
import xbmcgui
import xbmcaddon
import json
import platform
import re
import xbmcvfs

ADDON_NAME = xbmcaddon.Addon().getAddonInfo('name')
PATH = xbmcaddon.Addon().getAddonInfo('path')
PROFILE = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
LS = xbmcaddon.Addon().getLocalizedString

# Constants

STRING = 0
BOOL = 1
NUM = 2


def writeLog(message, level=xbmc.LOGDEBUG):
    xbmc.log('[%s %s] %s' % (xbmcaddon.Addon().getAddonInfo('id'),
                             xbmcaddon.Addon().getAddonInfo('version'),
                             message), level)


def notify(header, message, icon=xbmcgui.NOTIFICATION_INFO, dispTime=5000):
    xbmcgui.Dialog().notification(header, message, icon=icon, time=dispTime)


def release():
    item = dict()
    coll = {'platform': platform.system(), 'hostname': platform.node()}
    if coll['platform'] == 'Linux':
        with open('/etc/os-release', 'r') as _file:
            for _line in _file:
                parameter, value = _line.split('=')
                item[parameter] = value.replace('"', '').strip()

    coll.update({'osname': item.get('NAME', ''), 'osid': item.get('ID', ''), 'osversion': item.get('VERSION_ID', '')})
    return coll


def dialogOK(header, message):
    return xbmcgui.Dialog().ok(header, message)


def dialogYesNo(header, message):
    return xbmcgui.Dialog().yesno(header, message)


def dialogSelect(header, itemlist, preselect=-1, useDetails=False):
    return xbmcgui.Dialog().select(header, itemlist, preselect=preselect, useDetails=useDetails)


def jsonrpc(query):
    querystring = {"jsonrpc": "2.0", "id": 1}
    querystring.update(query)
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(querystring)))
        if 'result' in response: return response['result']
    except TypeError as e:
        writeLog('Error executing JSON RPC: %s' % (e), xbmc.LOGERROR)
    return None


def getAddonSetting(setting, sType=STRING, multiplicator=1):
    if sType == BOOL:
        return  True if xbmcaddon.Addon().getSetting(setting).upper() == 'TRUE' else False
    elif sType == NUM:
        try:
            return int(re.match('\d+', xbmcaddon.Addon().getSetting(setting)).group()) * multiplicator
        except AttributeError:
            return 0
    else:
        return xbmcaddon.Addon().getSetting(setting)
