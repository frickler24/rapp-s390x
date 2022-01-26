from django.http import HttpResponse
from django.utils.encoding import smart_str

from rapp.models import TblRollehataf
from rapp.view_UserHatRolle_Datenbeschaffung import UhR_erzeuge_listen_ohne_rollen, UhR_hole_daten
from .excel import Excel

def panel_UhR_af_export(request, id):
    """
    Exportfunktion für das Filter-Panel aus der "User und Rollen"-Tabelle).
    :param request: GET Request vom Browser
    :param id: id = 0: alle UserIDen, sonst wird nur nach der UserID mit der tabelleninternen ID = id gesucht
    :return: Gerendertes HTML mit den CSV-Daten oder eine Fehlermeldung
    """
    if request.method != 'GET':
        return HttpResponse("Fehlerhafte CSV-Generierung in panel_UhR_af_export")

    (namen_liste, panel_filter, rollen_liste, rollen_filter) = UhR_erzeuge_listen_ohne_rollen(request)
    (userHatRolle_liste, selektierter_name, userids, usernamen,
     selektierte_haupt_userid, selektierte_userids, afmenge, afmenge_je_userID) \
        = UhR_hole_daten(namen_liste, id)

    headline = [
        smart_str(u'Name'),
        smart_str(u'Rollenname'),
        smart_str(u'AF'),
        smart_str(u'Mussrecht')
    ]
    for userid in selektierte_userids:
        headline.append(smart_str(userid))

    excel = Excel("rollen.csv")
    excel.writerow(headline)

    for rolle in userHatRolle_liste:
        for rollendefinition in TblRollehataf.objects.filter(rollenname=rolle.rollenname):
            line = [selektierter_name, rolle.rollenname, rollendefinition.af]
            if rollendefinition.mussfeld is None:
                line.append('undef')
            else:
                if rollendefinition.mussfeld > 0:
                    line.append('ja')
                else:
                    line.append('nein')
            for userid in selektierte_userids:
                if str(rollendefinition.af).strip().lower() in str(afmenge_je_userID[userid]).lower():
                    line.append('ja')
                else:
                    line.append('nein')
            excel.writerow(line)

    return excel.response
