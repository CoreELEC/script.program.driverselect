from resources.lib.tools import *

writeLog('starting addon')
query = {"method": "Addons.GetAddons",
         "params": {"type": "xbmc.service",
                    "properties": ["name", "path", "enabled"]}}
response = jsonrpc(query)
if response is not None:
    writeLog('get services')

    addon_list = {}
    gui_list = []
    modules = []
    item = 0

    # get all services, discard services without driver.dvb signature

    for service in response['addons']:
        if not 'driver.dvb.' in service.get('addonid', ''): continue
        addon_list.update({item: {'name': service.get('name', ''),
                                'addonid': service.get('addonid', ''),
                                'enabled': service.get('enabled', False)}})
        if service.get('enabled', False):
            gui_list.append('[B]' + service.get('name', '') + '[/B]')
            modules.append(service.get('addonid'))
        else:
            gui_list.append(service.get('name', ''))
        item += 1

    # show selections

    if item > 0:
        driver_module = dialogSelect(LS(30011), gui_list)
        writeLog('selected item: %s' % (driver_module))

        if driver_module > -1:

            # disable old driver module(s)

            for dvbmodule in modules:
                query = {"method": "Addons.SetAddonEnabled",
                         "params":{"addonid": dvbmodule, "enabled": False}}
                response = jsonrpc(query)
                if response == 'OK':
                    writeLog('driver module \'%s\' disabled' % (dvbmodule))
                else:
                    writeLog('could not disable driver module \'%s\'' % (dvbmodule), xbmc.LOGFATAL)

            # enable new driver module

            query = {"method": "Addons.SetAddonEnabled",
                     "params": {"addonid": addon_list[driver_module]['addonid'], "enabled": True}}
            response = jsonrpc(query)
            if response == 'OK':
                writeLog('driver module \'%s\' enabled' % (addon_list[driver_module]['addonid']))

                # ask for reboot

                yesno = dialogYesNo(LS(30012), LS(30013))
                if yesno:
                    query = {"method": "System.Reboot",
                             "params":{}}
                    response = jsonrpc(query)
                    if response == 'OK':
                        writeLog('system will now reboot')
                    else:
                        writeLog('could not reboot', xbmc.LOGFATAL)
                else:
                    notify(LS(30010), LS(30014), icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                writeLog('could not enable driver module \'%s\'' % (addon_list[driver_module]['addonid']), xbmc.LOGFATAL)
    else:
        writeLog('no driver modules found', xbmc.LOGFATAL)
        notify(LS(30010), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)
