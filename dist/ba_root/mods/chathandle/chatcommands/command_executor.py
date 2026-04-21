# Released under the ARR License. See LICENSE for details.


from datetime import datetime

import _babase
import setting
from playersdata import pdata
from serverdata import serverdata
from .commands import normal_commands , management, fun , cheats, ATD_commands
from .commands import CoinCmds
import bascenev1 as bs
from .handlers import check_permissions
from .handlers import clientid_to_accountid

settings = setting.get_settings_data()


def command_type(command):
    """
    Checks The Command Type

    Parameters:
        command : str

    Returns:
        any
    """
    if command in normal_commands.Commands or command in normal_commands.CommandAliases:
        return "Normal"

    if command in management.Commands or command in management.CommandAliases:
        return "Manage"

    if command in fun.Commands or command in fun.CommandAliases:
        return "Fun"

    if command in cheats.Commands or command in cheats.CommandAliases:
        return "Cheats"

    if command in CoinCmds.Commands or command in CoinCmds.CommandAliases:
        try:
            CoinCmds.CoinCommands(command, arguments, clientid, accountid)
        except Exception as _ce:
            import logging
            logging.warning(f'CoinCmds error: {_ce}')
        return None

    if command in ATD_commands.Commands or command in ATD_commands.CommandAliases:
        return "NewCmds"



def _notify(clientid: int, success: bool) -> None:
    """إرسال DONE أو ACCESS DENIED — يتجنب clients=[-1]."""
    if success:
        msg, color = "\ue00cDONE\ue00c", (0, 1, 0)
    else:
        msg, color = "\ue00cACCESS DENIED\ue00c", (1, 0, 0)
    if clientid == -1:
        bs.broadcastmessage(msg, color=color, transient=True)
    else:
        bs.broadcastmessage(msg, color=color, transient=True, clients=[clientid])


def execute(msg, clientid):
    """
    Command Execution

    Parameters:
        msg : str
        clientid : int

    Returns:
        any
    """
    command = msg.lower().split(" ")[0].split("/")[1]
    arguments = msg.lower().split(" ")[1:]
    accountid = clientid_to_accountid(clientid)

    if command in CoinCmds.Commands or command in CoinCmds.CommandAliases:
        CoinCmds.CoinCommands(command, arguments, clientid, accountid)
        return None

    if command_type(command) == "Normal":
        normal_commands.ExcelCommand(command, arguments, clientid, accountid)

    elif command_type(command) == "Manage":
        if check_permissions(accountid, command, clientid):
            management.ExcelCommand(command, arguments, clientid, accountid)
            _notify(clientid, True)
        else:
            _notify(clientid, False)

    elif command_type(command) == "Fun":
        if check_permissions(accountid, command, clientid):
            fun.ExcelCommand(command, arguments, clientid, accountid)
            _notify(clientid, True)
        else:
            _notify(clientid, False)

    elif command_type(command) == "Cheats":
        if check_permissions(accountid, command, clientid):
            cheats.ExcelCommand(command, arguments, clientid, accountid)
            _notify(clientid, True)
        else:
            _notify(clientid, False)

    elif command_type(command) == "NewCmds":
        if check_permissions(accountid, command, clientid):
            ATD_commands.ExcelCommand(command, arguments, clientid, accountid)
            _notify(clientid, True)
        else:
            _notify(clientid, False)

    elif command_type(command) is None and (
            command in CoinCmds.Commands or command in CoinCmds.CommandAliases):
        CoinCmds.CoinCommands(command, arguments, clientid, accountid)

    now = datetime.now()
    if accountid in pdata.get_blacklist()[
        "muted-ids"] and now < datetime.strptime(
        pdata.get_blacklist()["muted-ids"][accountid]["till"],
        "%Y-%m-%d %H:%M:%S"):
        clients = None if clientid == -1 else [clientid]
        bs.broadcastmessage("You are on mute", transient=True, clients=clients)
        return None
    if serverdata.muted:
        return None
    if settings["ChatCommands"]["BrodcastCommand"]:
        return msg
    return None

def QuickAccess(msg, client_id):
    from bascenev1lib.actor import popuptext
    if msg.startswith(","):
        name = ""
        teamid = 0
        for i in bs.get_foreground_host_session().sessionplayers:
            if i.inputdevice.client_id == client_id:
                teamid = i.sessionteam.id
                name = i.getname(True)

        for i in bs.get_foreground_host_session().sessionplayers:
            if hasattr(i,
                       'sessionteam') and i.sessionteam and teamid == i.sessionteam.id and i.inputdevice.client_id != client_id:
                bs.broadcastmessage(name + ":" + msg[1:],
                                    clients=[i.inputdevice.client_id],
                                    color=(0.3, 0.6, 0.3), transient=True)

        return None
    elif msg.startswith("."):
        msg = msg[1:]
        msgAr = msg.split(" ")
        if len(msg) > 25 or int(len(msg) / 5) > len(msgAr):
            bs.broadcastmessage("msg/word length too long",
                                clients=[client_id], transient=True)
            return None
        msgAr.insert(int(len(msgAr) / 2), "\n")
        for player in _babase.get_foreground_host_activity().players:
            if player.sessionplayer.inputdevice.client_id == client_id and player.actor.exists() and hasattr(
                player.actor.node, "position"):
                pos = player.actor.node.position
                with bs.get_foreground_host_activity().context:
                    popuptext.PopupText(
                        " ".join(msgAr),
                        (pos[0], pos[1] + 1, pos[2])).autoretain()
                return None
        return None
