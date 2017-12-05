from resources.lib.tools import *
import os

ADDON_TYPE = 'xbmc.service'
SIGNATURES = ['driver.dvb.', 'driver.video.', 'driver.net.']

# Addon Id's in this list should not appear in driver selection menue
EXCLUDES = ['driver.dvb.sundtek-mediatv', 'driver.dvb.hdhomerun']

ICON_FALLBACK = os.path.join(xbmc.translatePath(PATH), 'resources', 'fallback.png')
ICON_DEFAULT = os.path.join(xbmc.translatePath(PATH), 'resources', 'default.png')

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
        item = 1

        liz = xbmcgui.ListItem(label=LS(30024), label2=LS(30025 + group), iconImage=ICON_DEFAULT)
        liz.setProperty('addonid', 'dummy')
        gui_list[group].append(liz)

        for module in modules['addons']:
            if not signature in module.get('addonid', '') or module.get('addonid', '') in EXCLUDES: continue
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

        writeLog('%s modules added to group %s' % (len(gui_list[group]) - 1, signature[:-1]))
        group += 1

    # build main list, discard empty module lists

    group = 0
    MainItems = []
    for items in gui_list:
        if len(items) > 1: MainItems.append(LS(30021 + group))
        group += 1

    if len(MainItems) > 0:
        # show main list (preselection)

        selectedMainItem = dialogSelect(LS(30020), MainItems)
        if selectedMainItem > -1:
            selectedModuleItem = dialogSelect(LS(30011), gui_list[selectedMainItem], preselect=selections[selectedMainItem], useDetails=True)
            if selectedModuleItem > -1 and selectedModuleItem != selections[selectedMainItem]:
                # disable all modules of module group
                for module in gui_list[selectedMainItem]:
                    if module.getProperty('addonid') != 'dummy': set_addon(module.getProperty('addonid'), False)
                # and enable the new one
                if gui_list[selectedMainItem][selectedModuleItem].getProperty('addonid') != 'dummy':
                    set_addon(gui_list[selectedMainItem][selectedModuleItem].getProperty('addonid'), True)
                    ask_for_reboot(0)
                else:
                    ask_for_reboot(1)
            else:
                writeLog('aborted or module doesn\'t changed, no further actions required')
    else:
        writeLog('no driver modules found')
        notify(LS(30010), LS(30015), xbmcgui.NOTIFICATION_WARNING)
else:
    writeLog('Could not access addon library', xbmc.LOGERROR)
    notify(LS(30010), LS(30019), icon=xbmcgui.NOTIFICATION_ERROR)
