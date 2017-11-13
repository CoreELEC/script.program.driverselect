from resources.lib.tools import *
import os

ADDON_TYPE = 'xbmc.service'
SIGNATURES = ['driver.dvb.', 'driver.video.', 'driver.net.']
ICON_FALLBACK = os.path.join(xbmc.translatePath(PATH), 'lib', 'fallback.png')

# functions


def reset_addon(module):
    query = {"method": "Addons.SetAddonEnabled",
             "params": {"addonid": module, "enabled": False}}
    response = jsonrpc(query)
    if response == 'OK':
        writeLog('driver module \'%s\' disabled' % (module), xbmc.LOGNOTICE)
        return True
    else:
        writeLog('could not disable driver module \'%s\'' % (module), xbmc.LOGERROR)
    return False


def ask_for_reboot(msgid):
    message = [LS(30013), LS(30018)]
    yesno = dialogYesNo(LS(30012), message[msgid])
    if yesno:
        query = {"method": "System.Reboot",
                 "params": {}}
        response = jsonrpc(query)
        if response == 'OK':
            writeLog('system will now reboot', xbmc.LOGNOTICE)
        else:
            writeLog('could not reboot', xbmc.LOGERROR)
    else:
        notify(LS(30010), LS(30014), icon=xbmcgui.NOTIFICATION_WARNING)
    return False

writeLog('starting addon', xbmc.LOGNOTICE)
query = {"method": "Addons.GetAddons",
         "params": {"type": ADDON_TYPE,
                    "properties": ["description", "enabled", "name", "path", "thumbnail", "version"]}}
services = jsonrpc(query)

if services is not None:
    writeLog('collect services')
    gui_list = []

    # collect all services, discard services without driver.*. signature

    driver_group = 0
    for signature in SIGNATURES:
        gui_list.append([])

        for service in services['addons']:
            if not signature in service.get('addonid', ''):
                writeLog('discard \'%s\'' % (service.get('addonid', 'unknown')))
                continue
            liz = xbmcgui.ListItem(label='%s V%s' % (service.get('name') or LS(30017), service.get('version') or '0.0.0'),
                                   label2=service.get('description') or LS(30016),
                                   iconImage=service.get('thumbnail', ICON_FALLBACK))
            liz.setProperty('driver_group', str(driver_group))
            liz.setProperty('addonid', service.get('addonid'))
            liz.setProperty('enabled', str(service.get('enabled', False)))
            liz.setProperty('name', service.get('name') or LS(30017))
            liz.setProperty('path', service.get('path'))
            gui_list[driver_group].append(liz)

        writeLog('%s services added to group %s' % (len(gui_list[driver_group]), signature[:-1]))
        driver_group += 1

    # show main list
    main_list = dialogSelect(LS(30020), [LS(30021), LS(30022), LS(30023), LS(30024)])
    if main_list > -1:
        if 0 <= main_list <= 2:
            if len(gui_list[main_list]) > 0:
                driver = dialogSelect(LS(30011), gui_list[main_list], useDetails=True)
            else:
                writeLog('no driver modules found', xbmc.LOGERROR)
                notify(LS(30010), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)
        else:
            # Disable all Modules

            for signature in SIGNATURES:
                for service in services['addons']:
                    if not signature in service.get('addonid', ''): continue
                    reset_addon(service)
            ask_for_reboot(1)

    '''
    # show list

    if len(gui_list) > 0:
        driver_module = dialogSelect(LS(30011), gui_list, preselect=preselection, useDetails=True)
        if driver_module > -1:
            writeLog('selected item: %s' % gui_list[driver_module].getProperty('addonid'), xbmc.LOGNOTICE)
            if driver_module != preselection:

                # disable old driver module(s)

                for dvbmodule in modules:
                    query = {"method": "Addons.SetAddonEnabled",
                             "params":{"addonid": dvbmodule, "enabled": False}}
                    response = jsonrpc(query)
                    if response == 'OK':
                        writeLog('driver module \'%s\' disabled' % (dvbmodule), xbmc.LOGNOTICE)
                    else:
                        writeLog('could not disable driver module \'%s\'' % (dvbmodule), xbmc.LOGERROR)

                # enable new driver module

                query = {"method": "Addons.SetAddonEnabled",
                         "params": {"addonid": gui_list[driver_module].getProperty('addonid'), "enabled": True}}
                response = jsonrpc(query)
                if response == 'OK':
                    writeLog('driver module \'%s\' enabled' % (gui_list[driver_module].getProperty('name')), xbmc.LOGNOTICE)
                    ask_for_reboot()

                else:
                    writeLog('could not enable driver module \'%s\'' % (gui_list[driver_module].getProperty('name')), xbmc.LOGERROR)
            else:
                writeLog('module doesn\'t changed, no further actions required')
        else:
            writeLog('selection aborted')
    else:
        writeLog('no driver modules found', xbmc.LOGERROR)
        notify(LS(30010), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)
    '''
