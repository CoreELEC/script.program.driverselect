from resources.lib.tools import *
import os

ADDON_TYPE = 'xbmc.service'
SIGNATURES = ['driver.dvb.', 'driver.video.', 'driver.net.']
ICON_FALLBACK = os.path.join(xbmc.translatePath(PATH), 'lib', 'fallback.png')

# functions


def set_addon(module, enabled):
    query = {"method": "Addons.SetAddonEnabled",
             "params": {"addonid": module, "enabled": enabled}}
    response = jsonrpc(query)
    if response == 'OK':
        writeLog('driver module \'%s\' %s' % (module, 'enabled' if enabled else 'disabled'), xbmc.LOGNOTICE)
        return True
    else:
        writeLog('could not %s driver module \'%s\'' % ('enable' if enabled else 'disable', module), xbmc.LOGERROR)
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

# main

writeLog('starting addon', xbmc.LOGNOTICE)
query = {"method": "Addons.GetAddons",
         "params": {"type": ADDON_TYPE,
                    "properties": ["description", "enabled", "name", "path", "thumbnail", "version"]}}
modules = jsonrpc(query)

if modules is not None:
    writeLog('collect modules')
    gui_list = []
    selections = []

    # collect all services, discard services without driver.*. signature

    group = 0
    for signature in SIGNATURES:
        gui_list.append([])
        selections.append(-1)
        item = 0

        liz = xbmcgui.ListItem(label=LS(30024), label2=LS(30025 + group), iconImage=ICON_FALLBACK)
        liz.setProperty('addonid', 'dummy')
        gui_list[group].append(liz)

        for module in modules['addons']:
            if not signature in module.get('addonid', ''): continue
            liz = xbmcgui.ListItem(label=module.get('name') or LS(30017),
                                   label2=module.get('description') or LS(30016),
                                   iconImage=module.get('thumbnail', ICON_FALLBACK))
            if module.get('enabled', False):
                selections[group] = item
            liz.setProperty('addonid', module.get('addonid'))
            liz.setProperty('enabled', str(module.get('enabled', False)))
            liz.setProperty('name', module.get('name') or LS(30017))
            liz.setProperty('path', module.get('path'))
            gui_list[group].append(liz)
            item += 1

        writeLog('%s modules added to group %s' % (len(gui_list[group]), signature[:-1]))
        group += 1

    # show main list (preselection)

    mainItem = dialogSelect(LS(30020), [LS(30021), LS(30022), LS(30023)])
    if mainItem > -1:
        if len(gui_list[mainItem]) > 1:
            moduleItem = dialogSelect(LS(30011), gui_list[mainItem], preselect=selections[mainItem], useDetails=True)
            if moduleItem > -1 and moduleItem != selections[mainItem]:
                # disable all modules of module group
                for module in gui_list[mainItem]:
                    if module.getProperty('addonid') != 'dummy': set_addon(module.getProperty('addonid'), False)
                # and enable the new one
                if gui_list[mainItem][moduleItem].getProperty('addonid') != 'dummy':
                    set_addon(gui_list[mainItem][moduleItem].getProperty('addonid'), True)
                    ask_for_reboot(0)
                else:
                    ask_for_reboot(1)
            else:
                writeLog('aborted or module doesn\'t changed, no further actions required')
        else:
            writeLog('no driver modules found', xbmc.LOGERROR)
            notify(LS(30010), LS(30015), icon=xbmcgui.NOTIFICATION_WARNING)

else:
    writeLog('Could not access addon library', xbmc.LOGERROR)
    notify(LS(30010), LS(), icon=xbmcgui.NOTIFICATION_ERROR)
