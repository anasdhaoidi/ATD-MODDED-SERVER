# Released under the ARR License. See LICENSE for details.

from playersdata import pdata

import bascenev1 as bs


def clientid_to_accountid(clientid):
    """Transform Clientid To Accountid"""
    for i in bs.get_game_roster():
        if i['client_id'] == clientid:
            return i['account_id']
    # fallback للـ host أو من لم يُجد في roster
    try:
        session = bs.get_foreground_host_session()
        for sp in session.sessionplayers:
            if sp.inputdevice.client_id == clientid:
                return sp.get_account_id()
    except Exception:
        pass
    return None


def check_permissions(accountid, command, clientid=None):
    """
    Checks The Permission To Player To Executive Command

    Parameters:
        accountid : str
        command : str
        clientid : int (optional)

    Returns:
        Boolean
    """
    # اللاعب المحلي (Host) دائماً client_id == -1
    if clientid == -1:
        return True

    roles = pdata.get_roles()

    if is_server(accountid):
        return True

    for role in roles:
        if accountid in roles[role]["ids"] and "ALL" in roles[role]["commands"]:
            return True

        elif accountid in roles[role]["ids"] and command in roles[role][
            "commands"]:
            return True
    return False


def is_server(accid):
    if accid is None:
        return False
    for i in bs.get_game_roster():
        if i['account_id'] == accid and i['client_id'] == -1:
            return True
    return False


def send(msg: str, clientid: int) -> None:
    """ترسل رسالة في party window للجميع."""
    import _bascenev1
    for line in str(msg).splitlines():
        if line.strip():
            try:
                _bascenev1.chatmessage(line)
            except Exception:
                pass
