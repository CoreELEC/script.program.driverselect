from resources.lib.tools import *

ADDON_TYPE = 'xbmc.service'
SIGNATURE = 'driver.dvb.'
ICON_FALLBACK = os.path.join(xbmc.translatePath(PATH), 'lib', 'fallback.png')

writeLog('starting addon', xbmc.LOGNOTICE)
query = {"method": "Addons.GetAddons",
         "params": {"type": ADDON_TYPE,
                    "properties": ["description", "enabled", "name", "path", "thumbnail", "version"]}}
response = jsonrpc(query)

if response is not None:
    writeLog('get services')

    gui_list = []
    modules = []
    item = 0
    preselection = -1

    # get all services, discard services without driver.dvb signature

    for service in response['addons']:
        if not SIGNATURE in service.get('addonid', ''): continue
        liz = xbmcgui.ListItem(label='%s V%s' % (service.get('name') or LS(30017), service.get('version') or '0.0.0'),
                               label2=service.get('description') or LS(30016),
                               iconImage=service.get('thumbnail', ICON_FALLBACK))
        liz.setProperty('addonid', service.get('addonid'))
        liz.setProperty('enabled', str(service.get('enabled', False)))
        liz.setProperty('name', service.get('name') or LS(30017))
        liz.setProperty('path', service.get('path'))
        gui_list.append(liz)

        # collect all activated modules

        if bool(service.get('enabled')):
            if preselection == -1:
                preselection = item
                writeLog('preselect item no. %s' % (item))
            modules.append(service.get('addonid'))

        item += 1

    # show selections

    if item > 0:
        driver_module = dialogSelect(LS(30011), gui_list, preselect=preselection, useDetails=True)
        if driver_module > -1:
            writeLog('selected item: %s' % gui_list[driver_module].getProperty('addonid'), xbmc.LOGNOTICE)

            # disable old driver module(s)

            for dvbmodule in modules:
                query = {"method": "Addons.SetAddonEnabled",
                         "params":{"addonid": dvbmodule, "enabled": False}}
                response = jsonrpc(query)
                if response == 'OK':
                    writeLog('driver module \'%s\' disabled' % (dvbmodule), xbmc.LOGNOTICE)
                else:
                    writeLog('could not disable driver module \'%s\'' % (dvbmodule), xbmc.LOGFATAL)

            # enable new driver module

            query = {"method": "Addons.SetAddonEnabled",
                     "params": {"addonid": gui_list[driver_module].getProperty('addonid'), "enabled": True}}
            response = jsonrpc(query)
            if response == 'OK':
                writeLog('driver module \'%s\' enabled' % (gui_list[driver_module].getProperty('name')), xbmc.LOGNOTICE)

                # ask for reboot

                yesno = dialogYesNo(LS(30012), LS(30013))
                if yesno:
                    query = {"method": "System.Reboot",
                             "params":{}}
                    response = jsonrpc(query)
                    if response == 'OK':
                        writeLog('system will now reboot', xbmc.LOGNOTICE)
                    else:
                        writeLog('could not reboot', xbmc.LOGFATAL)
                else:
                    notify(LS(30010), LS(30014), icon=xbmcgui.NOTIFICATION_WARNING)
            else:
                writeLog('could not enable driver module \'%s\'' % (gui_list[driver_module].getProperty('name')), xbmc.LOGFATAL)
        else:
            writeLog('selection aborted')
    else:
        writeLog('no driver modules found', xbmc.LOGFATAL)
        notify(LS(30010), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)
