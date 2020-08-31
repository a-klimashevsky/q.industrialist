﻿import time
import tzlocal
import math
import re

from datetime import datetime
from eve_sde_tools import get_yaml
from eve_sde_tools import get_item_name_by_type_id
from eve_sde_tools import get_basis_market_group_by_type_id
from eve_sde_tools import get_blueprint_manufacturing_materials
from eve_esi_tools import get_assets_location_name

import q_industrialist_settings
import q_logist_settings

g_local_timezone = tzlocal.get_localzone()


def __get_img_src(tp, sz):
    if q_industrialist_settings.g_use_filesystem_resources:
        return './3/Types/{}_{}.png'.format(tp, sz)
    else:
        return 'http://imageserver.eveonline.com/Type/{}_{}.png'.format(tp, sz)


def __get_icon_src(icon_id, sde_icon_ids):
    """
    see: https://forums.eveonline.com/t/eve-online-icons/78457/3
    """
    if str(icon_id) in sde_icon_ids:
        nm = sde_icon_ids[str(icon_id)]["iconFile"]
        if q_industrialist_settings.g_use_filesystem_resources:
            return './3/{}'.format(nm)
        else:  # https://everef.net/img/Icons/items/9_64_5.png
            return 'https://everef.net/img/{}'.format(nm)
    else:
        return ""


def __dump_header(glf, header_name):
    glf.write("""
<!doctype html>
<html lang="ru">
 <head>
 <!-- <meta charset="utf-8"> -->
 <meta http-equiv="X-UA-Compatible" content="IE=edge">
 <meta name="viewport" content="width=device-width, initial-scale=1">
<style type="text/css">
.icn24 { width:24px; height:24px; }
.icn32 { width:32px; height:32px; }
.icn64 { width:64px; height:64px; }
</style>
""")
    glf.write(
        ' <title>Q.Industrialist - {nm}</title>\n'
        ' <link rel="stylesheet" href="{bs_css}">\n'
        '</head>\n'
        '<body>\n'
        '<div class="page-header">\n'
        ' <h1>Q.Industrialist <small>{nm}</small></h1>\n'
        '</div>\n'
        '<script src="{jq_js}"></script>\n'
        '<script src="{bs_js}"></script>\n'.format(
            nm=header_name,
            bs_css='bootstrap/3.4.1/css/bootstrap.min.css' if q_industrialist_settings.g_use_filesystem_resources else 'https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous',
            jq_js='jquery/jquery-1.12.4.min.js' if q_industrialist_settings.g_use_filesystem_resources else 'https://code.jquery.com/jquery-1.12.4.min.js" integrity="sha384-nvAa0+6Qg9clwYCGGPpDQLVpLNn0fRaROjHqs13t4Ggj3Ez50XnGQqc/r8MhnRDZ" crossorigin="anonymous',
            bs_js='bootstrap/3.4.1/js/bootstrap.min.js' if q_industrialist_settings.g_use_filesystem_resources else 'https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js" integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd" crossorigin="anonymous'
        )
    )

def __dump_footer(glf):
    # Don't remove line below !
    glf.write('<p><small><small>Generated {dt}</small></br>\n'.format(
        dt=datetime.fromtimestamp(time.time(), g_local_timezone).strftime('%a, %d %b %Y %H:%M:%S %z')))
    glf.write("""</br>
&copy; 2020 Qandra Si &middot; <a class="inert" href="https://github.com/Qandra-Si/q.industrialist">GitHub</a> &middot; Data provided by <a class="inert" href="https://esi.evetech.net/">ESI</a> and <a class="inert" href="https://zkillboard.com/">zKillboard</a> &middot; Tips go to <a class="inert" href="https://zkillboard.com/character/2116129465/">Qandra Si</a></br>
</br>
<small>EVE Online and the EVE logo are the registered trademarks of CCP hf. All rights are reserved worldwide. All other trademarks are the property of their respective owners. EVE Online, the EVE logo, EVE and all associated logos and designs are the intellectual property of CCP hf. All artwork, screenshots, characters, vehicles, storylines, world facts or other recognizable features of the intellectual property relating to these trademarks are likewise the intellectual property of CCP hf.</small>
</small></p>""")
    # Don't remove line above !
    glf.write("</body></html>")


def __dump_any_into_modal_header(glf, name, unique_id=None, btn_size="btn-lg", btn_nm=None):
    name_merged = name.replace(' ', '') if unique_id is None else unique_id
    glf.write(
        '<!-- Button trigger for {nm} Modal -->\n'
        '<button type="button" class="btn btn-primary {btn_sz}" data-toggle="modal" data-target="#modal{nmm}">{btn_nm}</button>\n'
        '<!-- {nm} Modal -->\n'
        '<div class="modal fade" id="modal{nmm}" tabindex="-1" role="dialog" aria-labelledby="modal{nmm}Label">\n'
        ' <div class="modal-dialog" role="document">\n'
        '  <div class="modal-content">\n'
        '   <div class="modal-header">\n'
        '    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\n'
        '    <h4 class="modal-title" id="modal{nmm}Label">{nm}</h4>\n'
        '   </div>\n'
        '   <div class="modal-body">\n'.
        format(nm=name,
               nmm=name_merged,
               btn_sz=btn_size,
               btn_nm='Show {nm}'.format(nm=name) if btn_nm is None else btn_nm))


def __dump_any_into_modal_footer(glf):
    glf.write("""
   </div>
   <div class="modal-footer">
    <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
    <!-- <button type="button" class="btn btn-primary">Choose</button> -->
   </div>
  </div>
 </div>
</div>
""")


def __dump_wallet(glf, wallet_data):
    glf.write("{} ISK".format(wallet_data))


def __get_station_name(id):
    dict = get_yaml(2, 'sde/bsd/invUniqueNames.yaml', "    itemID: {}".format(id))
    if "itemName" in dict:
        return dict["itemName"]
    return ""


def __build_hangar_tree(blueprint_data, assets_data, names_data):
    locations = []
    for bp in blueprint_data:
        # location_id
        # References a station, a ship or an item_id if this blueprint is located within a container.
        # If the return value is an item_id, then the Character AssetList API must be queried to find
        # the container using the given item_id to determine the correct location of the Blueprint.
        location_id1 = int(bp["location_id"])
        found = False
        for l1 in locations:
            if l1["id"] == location_id1:
                found = True
                break
        if found:
            continue
        loc1 = {"id": location_id1}  # id, station_id, station_name
        for ass in assets_data:
            if ass["item_id"] == location_id1:
                if ass["location_type"] == "station":
                    location_id2 = int(ass["location_id"])
                    loc1.update({"station_id": location_id2, "type_id": ass["type_id"], "level": 1})
                    found = False
                    for l3 in locations:
                        if l3["id"] == location_id2:
                            found = True
                            break
                    if not found:
                        loc2 = {"id": location_id2, "station_id": ass["location_id"], "level": 0}
                        name2 = __get_station_name(location_id2)
                        if name2:
                            loc2.update({"station_name": name2})
                        locations.append(loc2)
        if "station_id" in loc1:  # контейнер с известным id на станции
            station_name1 = __get_station_name(loc1["station_id"])
            if station_name1:
                loc1.update({"station_name": station_name1})
            name1 = None
            for nm in names_data:
                if nm["item_id"] == location_id1:
                    name1 = nm["name"]
            if not (name1 is None):
                loc1.update({"item_name": name1})
        if not ("station_id" in loc1):  # станция с известным id
            name1 = __get_station_name(location_id1)
            if name1:
                loc1.update({"station_name": name1})
                loc1.update({"station_id": location_id1})
                loc1.update({"level": 0})
        locations.append(loc1)
    return locations


def __dump_blueprints(glf, blueprint_data, assets_data, names_data, type_ids):
    glf.write("""
<!-- BEGIN: collapsable group (stations) -->
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
""")

    locations = __build_hangar_tree(blueprint_data, assets_data, names_data)
    # debug: glf.write("<!-- {} -->\n".format(locations))
    for loc in locations:
        # level : loc["level"] : REQUIRED
        # type_id : loc["type_id"] : OPTIONAL
        # location_id : loc["id"] : REQUIRED
        location_id = int(loc["id"])
        glf.write(
            " <div class=\"panel panel-default\">\n"
            "  <div class=\"panel-heading\" role=\"tab\" id=\"heading{id}\">\n"
            "   <h4 class=\"panel-title\">\n".format(id=location_id)
        )
        if "item_name" in loc:
            location_name = loc["item_name"]
            if "station_name" in loc:
                location_name = "{} - {}".format(loc["station_name"], location_name)
        elif "station_name" in loc:
            location_name = loc["station_name"]
        elif "station_id" in loc:
            location_name = loc["station_id"]
        else:
            location_name = location_id
        glf.write("    <a role=\"button\" data-toggle=\"collapse\" data-parent=\"#accordion\" "
                  "href=\"#collapse{id}\" aria-expanded=\"true\" aria-controls=\"collapse{id}\""
                  ">{nm}</a>\n".format(id=location_id, nm=location_name))
        # if "type_id" in loc:  # у станции нет type_id, он есть только у item-ов (контейнеров)
        #     glf.write('<img src=\'./3/Types/{tp}_32.png\'/>'.format(tp=loc["type_id"]))
        glf.write(
            "   </h4>\n"
            "  </div>\n"
            "  <div id=\"collapse{id}\" class=\"panel-collapse collapse\" role=\"tabpanel\""
            "  aria-labelledby=\"heading{id}\">\n"
            "   <div class=\"panel-body\">\n".format(id=location_id)
        )
        # blueprints list
        for bp in blueprint_data:
            if bp["location_id"] != location_id:
                continue
            type_id = bp["type_id"]
            blueprint_name = get_item_name_by_type_id(type_ids, type_id)
            glf.write('<p><img class="icn32" src="{src}"/>{nm}</p>\n'.format(
                nm=blueprint_name,
                src=__get_img_src(type_id, 32)
            ))
        glf.write(
            "   </div>\n"
            "  </div>\n"
            " </div>\n"
        )

    glf.write("""
</div>
<!-- END: collapsable group (stations) -->
""")


def __dump_corp_blueprints(
        glf,
        corp_bp_loc_data,
        corp_industry_jobs_data,
        corp_ass_names_data,
        corp_ass_loc_data,
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        stock_all_loc_ids,
        blueprint_loc_ids,
        enable_copy_to_clipboard=False):
    # формирование списка ресурсов, которые используются в производстве
    stock_resources = {}
    if not (stock_all_loc_ids is None):
        for loc_id in stock_all_loc_ids:
            loc_flags = corp_ass_loc_data.keys()
            for loc_flag in loc_flags:
                __a1 = corp_ass_loc_data[loc_flag]
                if str(loc_id) in __a1:
                    __a2 = __a1[str(loc_id)]
                    for itm in __a2:
                        if str(itm) in stock_resources:
                            stock_resources[itm] = stock_resources[itm] + __a2[itm]
                        else:
                            stock_resources.update({itm: __a2[itm]})

    glf.write("""
<!-- BEGIN: collapsable group (locations) -->
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">""")

    loc_flags = corp_bp_loc_data.keys()
    for loc_flag in loc_flags:
        loc_ids = corp_bp_loc_data[str(loc_flag)].keys()
        for loc in loc_ids:
            loc_id = int(loc)
            if not (blueprint_loc_ids is None):
                if not (loc_id in blueprint_loc_ids):
                    continue
            loc_name = next((n["name"] for n in corp_ass_names_data if n['item_id'] == loc_id), loc_id)
            glf.write(
                ' <div class="panel panel-default">\n'
                '  <div class="panel-heading" role="tab" id="headingB{fl}{id}">\n'
                '   <h4 class="panel-title">\n'
                '    <a role="button" data-toggle="collapse" data-parent="#accordion" '
                '       href="#collapseB{fl}{id}" aria-expanded="true" aria-controls="collapseB{fl}{id}">{nm}</a>\n'
                '   </h4>\n'
                '  </div>\n'
                '  <div id="collapseB{fl}{id}" class="panel-collapse collapse" role="tabpanel" '
                'aria-labelledby="headingB{fl}{id}">\n'
                '   <div class="panel-body">\n'.format(
                    fl=loc_flag,
                    id=loc_id,
                    nm=loc_name
                )
            )
            __bp2 = corp_bp_loc_data[str(loc_flag)][str(loc_id)]
            type_keys = __bp2.keys()
            materials_summary = {}
            for type_id in type_keys:
                blueprint_name = get_item_name_by_type_id(sde_type_ids, type_id)
                glf.write(
                    '<div class="media">\n'
                    ' <div class="media-left">\n'
                    '  <img class="media-object icn64" src="{src}" alt="{nm}">\n'
                    ' </div>\n'
                    ' <div class="media-body">\n'
                    '  <h4 class="media-heading">{nm}</h4>\n'.format(
                        src=__get_img_src(type_id, 64),
                        nm=blueprint_name
                    )
                )
                bp_manuf_mats = get_blueprint_manufacturing_materials(sde_bp_materials, type_id)
                bp_keys = __bp2[type_id].keys()
                for bpk in bp_keys:
                    bp = __bp2[type_id][bpk]
                    is_blueprint_copy = bp["cp"]
                    quantity_or_runs = bp["qr"]
                    material_efficiency = bp["me"]
                    time_efficiency = bp["te"]
                    blueprint_status = bp["st"]
                    glf.write(
                        '<span class="qind-blueprints-{status}">'
                        '<span class="label label-{cpc}">{cpn}</span>'
                        '&nbsp;<span class="label label-success">{me} {te}</span>'
                        '&nbsp;<span class="badge">{qr}</span>\n'.format(
                            qr=quantity_or_runs,
                            cpc='default' if is_blueprint_copy else 'info',
                            cpn='copy' if is_blueprint_copy else 'original',
                            me=material_efficiency,
                            te=time_efficiency,
                            status=blueprint_status if not (blueprint_status is None) else ""
                        )
                    )
                    if not (blueprint_status is None):  # [ active, cancelled, delivered, paused, ready, reverted ]
                        if (blueprint_status == "active") or (blueprint_status == "delivered"):
                            glf.write('&nbsp;<span class="label label-info">{}</span>'.format(blueprint_status))
                        elif blueprint_status == "ready":
                            glf.write('&nbsp;<span class="label label-success">{}</span>'.format(blueprint_status))
                        elif (blueprint_status == "cancelled") or (blueprint_status == "paused") or (blueprint_status == "reverted"):
                            glf.write('&nbsp;<span class="label label-warning">{}</span>'.format(blueprint_status))
                        else:
                            glf.write('&nbsp;<span class="label label-danger">{}</span>'.format(blueprint_status))
                        glf.write('</br></span>\n')
                    elif bp_manuf_mats is None:
                        glf.write('&nbsp;<span class="label label-warning">manufacturing impossible</span>')
                        glf.write('</br></span>\n')
                    else:
                        glf.write('</br></span>\n')
                        glf.write('<div class="qind-materials-used">\n')  # div(materials)
                        not_enough_materials = []
                        for m in bp_manuf_mats:
                            bp_manuf_need_all = 0
                            for __bp3 in __bp2[type_id][bpk]["itm"]:
                                quantity_or_runs = __bp3["r"] if is_blueprint_copy else __bp3["q"] if __bp3["q"] > 0 else 1
                                __used = int(m["quantity"]) * quantity_or_runs  # сведения из чертежа
                                __need = __used  # поправка на эффективнсть материалов
                                if material_efficiency > 0:
                                    # TODO: хардкодим -1% structure role bonus, -4.2% installed rig
                                    # см. 1 x run: http://prntscr.com/u0g07w
                                    # см. 4 x run: http://prntscr.com/u0g0cd
                                    # см. экономия материалов: http://prntscr.com/u0g11u
                                    __me = int(100 - material_efficiency - 1 - 4.2)
                                    __need = int((__used * __me) / 100)
                                    if 0 != ((__used * __me) % 100):
                                        __need = __need + 1
                                bp_manuf_need_all = bp_manuf_need_all + __need
                            bpmm_tid = int(m["typeID"])
                            bpmm_tnm = get_item_name_by_type_id(sde_type_ids, bpmm_tid)
                            # проверка наличия имеющихся ресурсов для постройки по этому БП
                            not_available = bp_manuf_need_all
                            if m["typeID"] in stock_resources:
                                not_available = 0 if stock_resources[m["typeID"]] >= not_available else not_available - stock_resources[m["typeID"]]
                            # вывод наименования ресурса
                            glf.write(
                                '<span style="white-space:nowrap">'
                                '<img class="icn24" src="{src}"> {q:,d} x {nm} '
                                '</span>\n'.format(
                                    src=__get_img_src(bpmm_tid, 32),
                                    q=bp_manuf_need_all,
                                    nm=bpmm_tnm
                                )
                            )
                            # сохраняем недостающее кол-во материалов для производства по этому чертежу
                            if not_available > 0:
                                not_enough_materials.append({"id": bpmm_tid, "q": not_available, "nm": bpmm_tnm})
                            # сохраняем материалы для производства в список их суммарного кол-ва
                            if m["typeID"] in materials_summary:
                                materials_summary[m["typeID"]] = materials_summary[m["typeID"]] + bp_manuf_need_all
                            else:
                                materials_summary.update({m["typeID"]: bp_manuf_need_all})
                        glf.write('</div>\n')  # div(materials)
                        # отображение списка материалов, которых не хватает
                        if len(not_enough_materials) > 0:
                            glf.write('<div>\n')  # div(not_enough_materials)
                            for m in not_enough_materials:
                                glf.write(
                                    '&nbsp;<span class="label label-warning">'
                                    '<img class="icn24" src="{src}"> {q:,d} x {nm} '
                                    '</span>\n'.format(
                                        src=__get_img_src(m["id"], 32),
                                        q=m["q"],
                                        nm=m["nm"]
                                    )
                                )
                            glf.write('</div>\n')  # div(not_enough_materials)
                glf.write(
                    ' </div>\n'  # media-body
                    '</div>\n'  # media
                )
            # отображение в отчёте summary-информаци по недостающим материалам
            if len(materials_summary) > 0:
                ms_keys = materials_summary.keys()
                # поиск групп, которым принадлежат материалы, которых не хватает для завершения производства по списку
                # чертеже в этом контейнере (планетарка отдельно, композиты отдельно, запуск работ отдельно)
                material_groups = {}
                for ms_type_id in ms_keys:
                    __quantity = materials_summary[ms_type_id]
                    __market_group = get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, ms_type_id)
                    if str(__market_group) in material_groups:
                        material_groups[str(__market_group)].update({ms_type_id: __quantity})
                    else:
                        material_groups.update({str(__market_group): {ms_type_id: __quantity}})
                glf.write(
                    '<hr><div class="media">\n'
                    ' <div class="media-left">\n'
                    '  <span class="glyphicon glyphicon-alert" aria-hidden="false" style="font-size: 64px;"></span>\n'
                    ' </div>\n'
                    ' <div class="media-body">\n'
                    '  <div class="qind-materials-used">'
                    '  <h4 class="media-heading">Summary materials</h4>\n'
                )
                for ms_type_id in ms_keys:
                    glf.write(
                        '<span style="white-space:nowrap">'
                        '<img class="icn24" src="{src}"> {q:,d} x {nm} '
                        '</span>\n'.format(
                            src=__get_img_src(ms_type_id, 32),
                            q=materials_summary[ms_type_id],
                            nm=get_item_name_by_type_id(sde_type_ids, ms_type_id)
                        )
                    )
                glf.write('<hr></div>\n')  # qind-materials-used
                # вывод списка материалов, которых не хватает для завершения производства по списку чертежей
                not_available_row_num = 1
                ms_groups = material_groups.keys()
                for ms_group_id in ms_groups:
                    ms_keys = material_groups[ms_group_id].keys()
                    group_diplayed = False
                    for ms_type_id in ms_keys:
                        not_available = material_groups[ms_group_id][ms_type_id]
                        if ms_type_id in stock_resources:
                            not_available = 0 if stock_resources[ms_type_id] >= not_available else \
                                not_available - stock_resources[ms_type_id]
                        if not_available > 0:
                            if not_available_row_num == 1:
                                glf.write("""
<h4 class="media-heading">Not available materials</h4>
<div class="table-responsive">
<table class="table table-condensed">
<thead>
 <tr>
  <th style="width:40px;">#</th>
  <th>Materials</th>
  <th>Not available</th>
  <th>In progress</th>
 </tr>
</thead>
<tbody>
""")
                            if not group_diplayed:
                                __grp_name = sde_market_groups[ms_group_id]["nameID"]["en"]
                                glf.write(
                                    '<tr>\n'
                                    ' <td class="active" colspan="4"><strong>{nm}</strong><!--{id}--></td>\n'
                                    '</tr>'.
                                    format(nm=__grp_name, id=ms_group_id))
                                group_diplayed = True
                            jobs = [j for j in corp_industry_jobs_data if
                                        (j["product_type_id"] == ms_type_id) and
                                        (j['output_location_id'] in stock_all_loc_ids)]
                            in_progress = 0
                            for j in jobs:
                                in_progress = in_progress + j["runs"]
                            __item_name = get_item_name_by_type_id(sde_type_ids, ms_type_id)
                            __copy2clpbrd = '' if not enable_copy_to_clipboard else \
                                '&nbsp;<a data-target="#" role="button" data-copy="{nm}" class="qind-copy-btn"' \
                                '  data-toggle="tooltip"><span class="glyphicon glyphicon-copy"'\
                                '  aria-hidden="true"></span></a>'. \
                                format(nm=__item_name)
                            glf.write(
                                '<tr>\n'
                                ' <th scope="row">{num}</th>\n'
                                ' <td><img class="icn24" src="{src}"> {nm}{clbrd}</td>\n'
                                ' <td>{q:,d}</td>\n'
                                ' <td>{inp}</td>\n'
                                '</tr>'.
                                format(num=not_available_row_num,
                                       src=__get_img_src(ms_type_id, 32),
                                       q=not_available,
                                       inp='{:,d}'.format(in_progress) if in_progress > 0 else '',
                                       nm=__item_name,
                                       clbrd=__copy2clpbrd)
                            )
                            not_available_row_num = not_available_row_num + 1
                if not_available_row_num != 1:
                    glf.write("""
</tbody>
</table>
</div>
""")
                glf.write(
                    ' </div>\n'
                    '</div>\n'
                )
            glf.write(
                "   </div>\n"
                "  </div>\n"
                " </div>\n"
            )

    glf.write("""
</div>
<!-- END: collapsable group (locations) -->
""")


def __dump_corp_assets(glf, corp_ass_loc_data, corp_ass_names_data, type_ids):
    glf.write("""
<!-- BEGIN: collapsable group (locations) -->
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
""")

    loc_flags = corp_ass_loc_data.keys()
    for loc_flag in loc_flags:
        __a1 = corp_ass_loc_data[loc_flag]
        loc_ids = __a1.keys()
        for loc in loc_ids:
            loc_id = int(loc)
            loc_name = next((n["name"] for n in corp_ass_names_data if n['item_id'] == loc_id), loc_id)
            __a2 = __a1[str(loc_id)]
            type_keys = __a2.keys()
            glf.write(
                ' <div class="panel panel-default">\n'
                '  <div class="panel-heading" role="tab" id="headingA{fl}{id}">\n'
                '   <h4 class="panel-title">\n'
                '    <a role="button" data-toggle="collapse" data-parent="#accordion" '
                'href="#collapseA{fl}{id}" aria-expanded="true" aria-controls="collapseA{fl}{id}"'
                '>{fl} - {nm}</a> <span class="badge">{q}</span>\n'
                '   </h4>\n'
                '  </div>\n'
                '  <div id="collapseA{fl}{id}" class="panel-collapse collapse" role="tabpanel" '
                'aria-labelledby="headingA{fl}{id}">\n'
                '   <div class="panel-body">\n'.format(
                    fl=loc_flag,
                    id=loc_id,
                    nm=loc_name,
                    q=len(type_keys)
                )
            )
            for type_id in type_keys:
                item_name = get_item_name_by_type_id(type_ids, type_id)
                glf.write(
                    '<div class="media">\n'
                    ' <div class="media-left">\n'
                    '  <img class="media-object icn32" src="{src}" alt="{nm}">\n'
                    ' </div>\n'
                    ' <div class="media-body">\n'
                    '  <h4 class="media-heading">{nm} <span class="badge">{q}</span></h4>\n'
                    ' </div>\n'
                    '</div>\n'.format(
                        src=__get_img_src(type_id, 32),
                        nm=item_name,
                        q=__a2[type_id]
                    )
                )
            glf.write(
                "   </div>\n"
                "  </div>\n"
                " </div>\n"
            )

    glf.write("""
</div>
<!-- END: collapsable group (locations) -->
""")


def __dump_corp_assets_tree_nested(
        glf,
        location_id,
        corp_assets_data,
        corp_assets_tree,
        corp_ass_names_data,
        foreign_structures_data,
        eve_market_prices_data,
        sde_type_ids,
        sde_inv_names,
        sde_inv_items,
        sde_market_groups):
    region_id, region_name, loc_name, foreign = get_assets_location_name(
        location_id,
        sde_inv_names,
        sde_inv_items,
        corp_ass_names_data,
        foreign_structures_data)
    itm_dict = None
    loc_dict = corp_assets_tree[str(location_id)]
    type_id = loc_dict["type_id"] if "type_id" in loc_dict else None
    group_id = get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, type_id)
    items = loc_dict["items"] if "items" in loc_dict else None
    nested_quantity = None
    items_quantity = None
    base_price = None
    volume = None
    if not (items is None):
        nested_quantity = len(items)
    if itm_dict is None:
        itm_dict = next((a for a in corp_assets_data if a['item_id'] == location_id), None)
    if not (itm_dict is None):
        items_quantity = itm_dict["quantity"]
        if str(type_id) in sde_type_ids:
            __type_dict = sde_type_ids[str(type_id)]
            if "basePrice" in __type_dict:
                base_price = __type_dict["basePrice"] * items_quantity
            if "volume" in __type_dict:
                volume = __type_dict["volume"] * items_quantity
    if type_id is None:
        __price_dict = None
    else:
        __price_dict = next((p for p in eve_market_prices_data if p['type_id'] == int(type_id)), None)
    glf.write(
        '<div class="media">\n'
        ' <div class="media-left media-top">{img}</div>\n'
        ' <div class="media-body">\n'
        '  <h4 class="media-heading">{where}{what}{iq}{nq}</h4>\n'
        '  <span class="label label-info">{id}</span>{loc_flag}{foreign}\n'
        '  {grp}{base}{average}{adjusted}{volume}\n'.
        format(
            img='<img class="media-object icn32" src="{src}">'.format(src=__get_img_src(type_id, 32)) if not (type_id is None) else "",
            where='{} '.format(loc_name) if not (loc_name is None) else "",
            what='<small>{}</small> '.format(get_item_name_by_type_id(sde_type_ids, type_id)) if not (type_id is None) else "",
            id=location_id,
            nq=' <span class="badge">{}</span>'.format(items_quantity) if not (items_quantity is None) and (items_quantity > 1) else "",
            iq=' <span class="label label-info">{}</span>'.format(nested_quantity) if not (nested_quantity is None) and (nested_quantity > 1) else "",
            loc_flag=' <span class="label label-default">{}</span>'.format(itm_dict["location_flag"]) if not (itm_dict is None) else "",
            foreign='<br/><span class="label label-warning">foreign</span>' if foreign else "",
            grp='</br><span class="label label-success">{}</span>'.format(sde_market_groups[str(group_id)]["nameID"]["en"]) if not (group_id is None) else "",
            base='</br>base: {:,.1f} ISK'.format(base_price) if not (base_price is None) else "",
            average='</br>average: {:,.1f} ISK'.format(__price_dict["average_price"]*items_quantity) if not (items_quantity is None) and not (__price_dict is None) and ("average_price" in __price_dict) else "",
            adjusted='</br>adjusted: {:,.1f} ISK'.format(__price_dict["adjusted_price"]*items_quantity) if not (items_quantity is None) and not (__price_dict is None) and ("adjusted_price" in __price_dict) else "",
            volume='</br>{:,.1f} m&sup3'.format(volume) if not (volume is None) else ""
        )
    )
    if not (items is None):
        for itm in items:
            __dump_corp_assets_tree_nested(
                glf,
                itm,
                corp_assets_data,
                corp_assets_tree,
                corp_ass_names_data,
                foreign_structures_data,
                eve_market_prices_data,
                sde_type_ids,
                sde_inv_names,
                sde_inv_items,
                sde_market_groups)
    glf.write(
        ' </div>\n'
        '</div>\n'
    )


def __dump_corp_assets_tree(
        glf,
        corp_assets_data,
        corp_assets_tree,
        corp_ass_names_data,
        foreign_structures_data,
        eve_market_prices_data,
        sde_type_ids,
        sde_inv_names,
        sde_inv_items,
        sde_market_groups):
    glf.write("""
<!-- BEGIN: collapsable group (locations) -->
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
  <ul class="media-list">
    <li class="media">""")

    if "roots" in corp_assets_tree:
        roots = corp_assets_tree["roots"]
        for loc_id in roots:
            __dump_corp_assets_tree_nested(
                glf,
                loc_id,
                corp_assets_data,
                corp_assets_tree,
                corp_ass_names_data,
                foreign_structures_data,
                eve_market_prices_data,
                sde_type_ids,
                sde_inv_names,
                sde_inv_items,
                sde_market_groups)

    glf.write("""    </li>
  </ul>
</div>
<!-- END: collapsable group (locations) -->
""")


def dump_industrialist_into_report(
        ws_dir,
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        wallet_data,
        blueprint_data,
        assets_data,
        asset_names_data,
        corp_industry_jobs_data,
        corp_ass_names_data,
        corp_ass_loc_data,
        corp_bp_loc_data,
        stock_all_loc_ids,
        blueprint_loc_ids):
    glf = open('{dir}/report.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Workflow")

        __dump_any_into_modal_header(glf, "Wallet")
        __dump_wallet(glf, wallet_data)
        __dump_any_into_modal_footer(glf)

        __dump_any_into_modal_header(glf, "Blueprints")
        __dump_blueprints(glf, blueprint_data, assets_data, asset_names_data, sde_type_ids)
        __dump_any_into_modal_footer(glf)

        __dump_any_into_modal_header(glf, "Corp Blueprints")
        __dump_corp_blueprints(glf, corp_bp_loc_data, corp_industry_jobs_data, corp_ass_names_data, corp_ass_loc_data, sde_type_ids, sde_bp_materials, sde_market_groups, stock_all_loc_ids, blueprint_loc_ids)
        __dump_any_into_modal_footer(glf)

        __dump_any_into_modal_header(glf, "Corp Assets")
        __dump_corp_assets(glf, corp_ass_loc_data, corp_ass_names_data, sde_type_ids)
        __dump_any_into_modal_footer(glf)

        __dump_footer(glf)
    finally:
        glf.close()


def __dump_materials(glf, materials, type_ids):
    for type_id in materials:
        sid = str(type_id)
        if not (sid in type_ids):
            material_name = sid
        else:
            material_name = type_ids[sid]["name"]["en"]
        glf.write('<p><img src="{src}"/>{nm} ({tp})</p>\n'.format(src=__get_img_src(type_id, 32), nm=material_name, tp=type_id))


def __dump_bp_wo_manufacturing(glf, blueprints, type_ids):
    for type_id in blueprints:
        sid = str(type_id)
        if not (sid in type_ids):
            material_name = sid
        else:
            material_name = type_ids[sid]["name"]["en"]
        glf.write('<p><img src="{src}">{nm} ({tp})</p>\n'.format(src=__get_img_src(type_id, 32), nm=material_name, tp=type_id))


def __dump_bp_wo_materials(glf, blueprints, type_ids):
    for type_id in blueprints:
        sid = str(type_id)
        if not (sid in type_ids):
            material_name = sid
        else:
            material_name = type_ids[sid]["name"]["en"]
        glf.write('<p><img src="{src}"/>{nm} ({tp})</p>\n'.format(src=__get_img_src(type_id, 32), nm=material_name, tp=type_id))


def dump_materials_into_report(ws_dir, sde_type_ids, materials, wo_manufacturing, wo_materials):
    glf = open('{dir}/materials.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Materials")

        __dump_any_into_modal_header(glf, "All Possible Materials")
        __dump_materials(glf, materials, sde_type_ids)
        __dump_any_into_modal_footer(glf)

        __dump_any_into_modal_header(glf, "Impossible to Produce Blueprints")
        __dump_bp_wo_manufacturing(glf, wo_manufacturing, sde_type_ids)
        __dump_any_into_modal_footer(glf)

        __dump_any_into_modal_header(glf, "Blueprints without Materials")
        __dump_bp_wo_materials(glf, wo_materials, sde_type_ids)
        __dump_any_into_modal_footer(glf)

        __dump_footer(glf)
    finally:
        glf.close()


def dump_assets_tree_into_report(
        ws_dir,
        sde_type_ids,
        sde_inv_names,
        sde_inv_items,
        sde_market_groups,
        corp_assets_data,
        corp_ass_names_data,
        foreign_structures_data,
        eve_market_prices_data,
        corp_assets_tree):
    glf = open('{dir}/assets_tree.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Corp Assets")

        __dump_any_into_modal_header(glf, "Corp Assets")
        __dump_corp_assets_tree(glf, corp_assets_data, corp_assets_tree, corp_ass_names_data, foreign_structures_data, eve_market_prices_data, sde_type_ids, sde_inv_names, sde_inv_items, sde_market_groups)
        __dump_any_into_modal_footer(glf)

        __dump_footer(glf)
    finally:
        glf.close()


def __get_route_signalling_type(level):
    if level == 0:
        return "success"
    elif level == 1:
        return "warning"
    elif (level == 2) or (level == 3):
        return "danger"


def __dump_corp_cynonetwork(glf, sde_inv_positions, corp_cynonetwork):
    glf.write("""
<style>
.dropdown-submenu {
  position: relative;
}
.dropdown-submenu .dropdown-menu {
  top: 0;
  left: 100%;
  margin-top: -1px;
}
</style>

<nav class="navbar navbar-default">
 <div class="container-fluid">
  <div class="navbar-header">
   <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse" aria-expanded="false">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
   </button>
   <a class="navbar-brand" data-target="#"><span class="glyphicon glyphicon-random" aria-hidden="true"></span></a>
  </div>
   
  <div class="collapse navbar-collapse" id="bs-navbar-collapse">
   <ul class="nav navbar-nav">
    <li class="dropdown">
     <a data-target="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Routes <span class="caret"></span></a>
      <ul class="dropdown-menu">""")
    cynonet_num = 1
    for cn in q_logist_settings.g_cynonetworks:
        cn_route = cn["route"]
        from_id = cn_route[0]
        from_name = corp_cynonetwork[str(from_id)]["solar_system"]
        to_id = cn_route[-1]
        to_name = corp_cynonetwork[str(to_id)]["solar_system"]
        glf.write(
            '\n       '
            '<li><a id="btnCynoNetSel" cynonet="{cnn}" data-target="#" role="button"><span '
                   'class="glyphicon glyphicon-star img-cyno-net" cynonet="{cnn}" aria-hidden="true"></span> '
            '{f} &rarr; {t}</a></li>'.  # предполагается: <li><a>JK-Q77 &rarr; Raravath</a></li>
            format(f=from_name,
                   t=to_name,
                   cnn=cynonet_num
            ))
        cynonet_num = cynonet_num + 1
    glf.write("""
       <li role="separator" class="divider"></li>
       <li><a id="btnCynoNetSel" cynonet="0" data-target="#" role="button"><span 
              class="glyphicon glyphicon-star img-cyno-net" cynonet="0" aria-hidden="true"></span> All routes</a></li>
     </ul>
    </li>
    
    <li class="dropdown">
     <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Jump Options <span class="caret"></span></a>
      <ul class="dropdown-menu">

       <li class="dropdown-submenu">
         <a class="options-submenu" data-target="#" role="button">Ship <mark id="lbJumpShip"></mark><span class="caret"></span></a>
         <ul class="dropdown-menu">
           <li class="dropdown-header">[Jump Freighters]</li>
           <li><a id="btnJumpShip" ship="Anshar" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpShipAnshar"></span> Anshar</a></li>
           <li><a id="btnJumpShip" ship="Ark" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpShipArk"></span> Ark</a></li>
           <li><a id="btnJumpShip" ship="Nomad" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpShipNomad"></span> Nomad</a></li>
           <li><a id="btnJumpShip" ship="Rhea" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpShipRhea"></span> Rhea</a></li>
           <li role="separator" class="divider"></li>
           <li><a id="btnJumpAnyShip" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpAnyShip"></span> Any Ship</a></li>
         </ul>
       </li>

       <li class="dropdown-submenu">
         <a class="options-submenu" data-target="#" role="button">Jump Drive Calibration <mark id="lbJumpCalibration"></mark><span class="caret"></span></a>
         <ul class="dropdown-menu">
           <li><a id="btnJumpCalibration" skill="1" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpCalibration1"></span> 1</a></li>
           <li><a id="btnJumpCalibration" skill="2" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpCalibration2"></span> 2</a></li>
           <li><a id="btnJumpCalibration" skill="3" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpCalibration3"></span> 3</a></li>
           <li><a id="btnJumpCalibration" skill="4" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpCalibration4"></span> 4</a></li>
           <li><a id="btnJumpCalibration" skill="5" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpCalibration5"></span> 5</a></li>
         </ul>
       </li>

       <li class="dropdown-submenu">
         <a class="options-submenu" data-target="#" role="button">Jump Drive Conservation <mark id="lbJumpConservation"></mark><span class="caret"></span></a>
         <ul class="dropdown-menu">
           <li><a id="btnJumpConservation" skill="1" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpConservation1"></span> 1</a></li>
           <li><a id="btnJumpConservation" skill="2" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpConservation2"></span> 2</a></li>
           <li><a id="btnJumpConservation" skill="3" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpConservation3"></span> 3</a></li>
           <li><a id="btnJumpConservation" skill="4" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpConservation4"></span> 4</a></li>
           <li><a id="btnJumpConservation" skill="5" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpConservation5"></span> 5</a></li>
         </ul>
       </li>

       <li class="dropdown-submenu">
         <a class="options-submenu" data-target="#" role="button">Jump Freighter <mark id="lbJumpFreighter"></mark><span class="caret"></span></a>
         <ul class="dropdown-menu">
           <li><a id="btnJumpFreighter" skill="1" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpFreighter1"></span> 1</a></li>
           <li><a id="btnJumpFreighter" skill="2" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpFreighter2"></span> 2</a></li>
           <li><a id="btnJumpFreighter" skill="3" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpFreighter3"></span> 3</a></li>
           <li><a id="btnJumpFreighter" skill="4" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpFreighter4"></span> 4</a></li>
           <li><a id="btnJumpFreighter" skill="5" class="option" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgJumpFreighter5"></span> 5</a></li>
         </ul>
       </li>

       <li role="separator" class="divider"></li>
       <li><a id="btnResetOptions" data-target="#" role="button">Reset options</a></li>
      </ul>
    </li>
    
    <li class="disabled"><a data-target="#" role="button">Problems</a></li>
   </ul>
   <form class="navbar-form navbar-right">
    <div class="form-group">
     <input type="text" class="form-control" placeholder="Solar System" disabled>
    </div>
    <button type="button" class="btn btn-default disabled">Search</button>
   </form>
  </div>
 </div>
</nav>
<div class="container-fluid">""")

    cynonetwork_num = 0
    cynonetwork_distances = []
    for cn in q_logist_settings.g_cynonetworks:
        cynonetwork_num = cynonetwork_num + 1
        cn_route = cn["route"]
        # from_name = ""
        # to_name = ""
        url = ""
        human_readable = ""
        route_signalling_level = 0
        for location_id in cn_route:
            route_place = corp_cynonetwork[str(location_id)]
            system_name = route_place["solar_system"]
            if not url:
                url = system_name
                # from_name = system_name
                human_readable = system_name
            else:
                url = url + ":" + system_name
                # to_name = system_name
                human_readable = human_readable + " &rarr; " + system_name
            route_signalling_level = max(route_signalling_level, route_place["signalling_level"])
        route_signalling_type = __get_route_signalling_type(route_signalling_level)
        # ---
        glf.write(
            '<div class="panel panel-{signal} pn-cyno-net" cynonet="{cnn}">\n'
            ' <div class="panel-heading"><h3 class="panel-title">{signal_sign}{nm}</h3></div>\n'
            '  <div class="panel-body">\n'
            '   <p>Checkout Dotlan link for graphical route building: <a class="lnk-dtln" cynonet="{cnn}" routes="{rs}" href="https://evemaps.dotlan.net/jump/Rhea,544/{url}" class="panel-link">https://evemaps.dotlan.net/jump/Rhea,544/{url}</a></p>\n'
            '   <div class="progress">\n'.
            format(#nm='{} &rarr; {}'.format(from_name, to_name),
                   cnn=cynonetwork_num,
                   rs=len(cn_route),
                   nm=human_readable,
                   url=url,
                   signal=route_signalling_type,
                   signal_sign='<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' if route_signalling_type=="danger" else ""
            ))
        progress_segments = len(cn_route)
        progress_width = int(100/progress_segments)
        progress_times = 1
        for location_id in cn_route:
            route_place = corp_cynonetwork[str(location_id)]
            system_name = route_place["solar_system"]
            if progress_times == progress_segments:
                progress_width = progress_width + 100 - progress_width * progress_segments
            if not ("error" in route_place):
                glf.write(
                    '    <div id="prgrCynoRoute{cnn}_{pt}" class="progress-bar progress-bar-{signal} signal" role="progressbar" style="width:{width}%">{nm}</div>\n'.
                    format(width=progress_width,
                           nm=system_name,
                           signal=__get_route_signalling_type(route_place["signalling_level"]),
                           cnn=cynonetwork_num,
                           pt=progress_times
                    ))
            else:
                glf.write(
                    '    <div class="progress-bar signal" role="progressbar" style="width:{width}%; background-color:#888;">{nm}</div>\n'.
                    format(width=progress_width,
                           nm=system_name
                    ))
            progress_times = progress_times + 1
        glf.write("""   </div>
   <table class="table">
    <thead>
     <tr>
      <th>#</th>
      <th>Solar System</th>
      <th><img src="https://imageserver.eveonline.com/Type/648_32.png" width="32px" height="32px" alt="Badger"/></th>
      <th><img src="https://imageserver.eveonline.com/Type/32880_32.png" width="32px" height="32px" alt="Venture"/><img
               src="https://imageserver.eveonline.com/Type/1317_32.png" width="32px" height="32px" alt="Expanded Cargohold I"/><img
               src="https://imageserver.eveonline.com/Type/31117_32.png" width="32px" height="32px" alt="Small Cargohold Optimization I"/></th>
      <th><img src="https://imageserver.eveonline.com/Type/52694_32.png" width="32px" height="32px" alt="Industrial Cynosural Field Generator"/></th>
      <th><img src="https://imageserver.eveonline.com/Type/16273_32.png" width="32px" height="32px" alt="Liquid Ozone"/></th>
      <th class="nitrogen">Nitrogen</th><th class="hydrogen">Hydrogen</th><th class="oxygen">Oxygen</th><th class="helium">Helium</th>
     </tr>
    </thead>
    <tbody>""")
        # --- расчёт дистанции прыжка
        prev_system_id = None
        row_num = 1
        lightyear_distances = []
        for location_id in cn_route:
            route_place = corp_cynonetwork[str(location_id)]
            system_id = route_place["system_id"]
            if row_num > 1:
                pos1 = sde_inv_positions[str(system_id)] if not (system_id is None) and (str(system_id) in sde_inv_positions) else None
                pos2 = sde_inv_positions[str(prev_system_id)] if not (prev_system_id is None) and (str(prev_system_id) in sde_inv_positions) else None
                if not (pos1 is None) and not (pos2 is None):
                    # https://en.wikipedia.org/wiki/Euclidean_distance
                    distance = math.sqrt((pos1["x"]-pos2["x"]) ** 2 + (pos1["y"]-pos2["y"]) ** 2 + (pos1["z"]-pos2["z"]) ** 2)
                    # https://github.com/nikdoof/cynomap
                    # ...Distance calculation is based on CCP's lightyear being 9460000000000000 meters, instead of
                    # the actual value of 9460730472580800 meters...
                    distance = distance / 9460000000000000
                    lightyear_distances.append(distance)  # lightyears
                    # https://wiki.eveuniversity.org/Jump_drives#Jumpdrive_Isotope_Usage_Formula
                    # ... moved to javascript logic ...
                else:
                    lightyear_distances.append(None)
            prev_system_id = system_id
            row_num = row_num + 1
        cynonetwork_distances.append(lightyear_distances)
        # --- построение таблицы по маршруту циносети
        row_num = 1
        for location_id in cn_route:
            route_place = corp_cynonetwork[str(location_id)]
            system_name = route_place["solar_system"]
            lightyears = lightyear_distances[row_num-1] if row_num < len(cn_route) else None
            if not ("error" in route_place) or (route_place["error"] != "no data"):
                badger_num = route_place["badger"]
                venture_num = route_place["venture"]
                liquid_ozone_num = route_place["liquid_ozone"]
                indus_cyno_gen_num = route_place["indus_cyno_gen"]
                exp_cargohold_num = route_place["exp_cargohold"]
                cargohold_rigs_num = route_place["cargohold_rigs"]
                nitrogen_isotope_num = route_place["nitrogen_isotope"]
                hydrogen_isotope_num = route_place["hydrogen_isotope"]
                oxygen_isotope_num = route_place["oxygen_isotope"]
                helium_isotope_num = route_place["helium_isotope"]
                badger_jumps_num = min(badger_num, indus_cyno_gen_num, int(liquid_ozone_num/950))
                venture_jumps_num = min(venture_num, indus_cyno_gen_num, int(liquid_ozone_num/200), exp_cargohold_num, int(cargohold_rigs_num/3))
                glf.write(
                    '<tr id="rowCynoRoute{cnn}_{num}" system="{nm}">\n'
                    ' <th scope="row">{num}</th><td>{nm}</td>\n'
                    ' <td><abbr title="{bjumps} Badger cynos">{b:,d}</abbr></td>\n'
                    ' <td><abbr title="{vjumps} Venture cynos">{v:,d}</abbr> / {ch:,d} / {chr:,d}</td>\n'
                    ' <td>{icg:,d}</td><td>{lo:,d}</td>\n'
                    ' <td class="nitrogen" id="niCynoRoute{cnn}_{num}">{ni:,d}</td>\n'
                    ' <td class="hydrogen" id="hyCynoRoute{cnn}_{num}">{hy:,d}</td>\n'
                    ' <td class="oxygen" id="oxCynoRoute{cnn}_{num}">{ox:,d}</td>\n'
                    ' <td class="helium" id="heCynoRoute{cnn}_{num}">{he:,d}</td>\n'
                    '</tr>'.
                    format(num=row_num,
                           cnn=cynonetwork_num,
                           nm=system_name,
                           bjumps=badger_jumps_num,
                           vjumps=venture_jumps_num,
                           b=badger_num,
                           v=venture_num,
                           lo=liquid_ozone_num,
                           icg=indus_cyno_gen_num,
                           ch=exp_cargohold_num,
                           chr=cargohold_rigs_num,
                           ni=nitrogen_isotope_num,
                           hy=hydrogen_isotope_num,
                           ox=oxygen_isotope_num,
                           he=helium_isotope_num
                    ))
            else:
                glf.write(
                    '<tr>\n'
                    ' <th scope="row">{num}</th><td>{nm}</td>\n'
                    ' <td></td><td></td><td></td><td></td><td></td>\n'
                    '</tr>'.
                    format(num=row_num,
                           nm=system_name))
            if row_num != len(cn_route):
                glf.write(
                    '<tr class="active">\n'
                    ' <th></th><td></td>\n'
                    ' <td colspan="4">{ly}</td><td colspan="4"{ly_val} cynonet="{cnn}" route="{rt}"></td>\n'
                    '</tr>'.
                    format(
                        ly_val=' lightyears="{:0.15f}"'.format(lightyears) if not (lightyears is None) else "",
                        cnn=cynonetwork_num,
                        rt=row_num,
                        ly='Distance: <strong>{:0.3f} ly</strong>'.format(lightyears) if not (lightyears is None) else ""
                    ))
            row_num = row_num + 1
        glf.write("""    </tbody>
   </table>
  </div>
 </div>""")
    glf.write("""<hr/>
<h4>Legend</h4>
  <div class="row">
   <div class="col-xs-3">
    <div class="progress">
     <div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="95" aria-valuemin="0" aria-valuemax="100" style="width: 95%;"></div>
    </div>
   </div>
   <div class="col-xs-9">10 or more jumps</div>
  </div>

  <div class="row">
   <div class="col-xs-3">
    <div class="progress">
     <div class="progress-bar progress-bar-warning" role="progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" style="width: 25%;"></div>
    </div>
   </div>
   <div class="col-xs-9">at least 2 jumps</div>
  </div>

  <div class="row">
   <div class="col-xs-3">
    <div class="progress">
     <div class="progress-bar progress-bar-danger" role="progressbar" aria-valuenow="10" aria-valuemin="0" aria-valuemax="100" style="width: 10%;"></div>
    </div>
   </div>
   <div class="col-xs-9">there is a chance to stop</div>
  </div>

  <div class="row">
   <div class="col-xs-3">
    <div class="progress">
     <div class="progress-bar" role="progressbar" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" style="width: 50%; background-color:#888;"></div>
    </div>
   </div>
   <div class="col-xs-9">there are temporary problems with ESI (out of sync assets movements)</div>
  </div>
</div>
<script>
  // Cynonetwork contents (data)
  var contentsCynoNetwork = [
""")
    # выгрузка данных для работы с ними с пом. java-script-а (повторный прогон с накопленными данными)
    cynonetwork_num = 1
    for cn in q_logist_settings.g_cynonetworks:
        glf.write('    [{cnn}, [\n'.format(cnn=cynonetwork_num))
        cn_route = cn["route"]
        route_num = 1
        for location_id in cn_route:
            last_route = route_num == len(cn_route)
            route_place = corp_cynonetwork[str(location_id)]
            system_name = route_place["solar_system"]
            lightyears = 0 if last_route else cynonetwork_distances[cynonetwork_num - 1][route_num - 1]
            if not lightyears:
                lightyears = 0
            if not ("error" in route_place) or (route_place["error"] != "no data"):
                nitrogen_isotope_num = route_place["nitrogen_isotope"]
                hydrogen_isotope_num = route_place["hydrogen_isotope"]
                oxygen_isotope_num = route_place["oxygen_isotope"]
                helium_isotope_num = route_place["helium_isotope"]
            else:
                nitrogen_isotope_num = 0
                hydrogen_isotope_num = 0
                oxygen_isotope_num = 0
                helium_isotope_num = 0
            if not ("error" in route_place):
                glf.write("      [{rn},'{nm}','{signal}',{ly},{ni},{hy},{ox},{he}]{comma}\n".
                          format(comma=',' if not last_route else ']',
                                 rn=route_num,
                                 nm=system_name,
                                 signal=__get_route_signalling_type(route_place["signalling_level"]),
                                 ni=nitrogen_isotope_num,
                                 hy=hydrogen_isotope_num,
                                 ox=oxygen_isotope_num,
                                 he=helium_isotope_num,
                                 ly=lightyears))
            route_num = route_num + 1
        glf.write('    ]{comma}\n'.format(comma=',' if cynonetwork_num != len(q_logist_settings.g_cynonetworks) else ''))
        cynonetwork_num = cynonetwork_num + 1
    # крупный листинг с java-программой (без форматирования)
    glf.write("""  ];
  // Jump Options storage (prepare)
  ls = window.localStorage;
  var knownShips = ['Anshar', 'Ark', 'Nomad', 'Rhea'];
  var usedIsotopeTags = ['th', 'td', 'span'];

  // Tools & Utils
  function numLikeEve(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  // Jump Options storage (init)
  function resetOptionsMenuToDefault() {
    if (!ls.getItem('CynoNetNum')) {
      ls.setItem('CynoNetNum', 0);
    }
    if (!ls.getItem('Jump Drive Calibration')) {
      ls.setItem('Jump Drive Calibration', 5);
    }
    if (!ls.getItem('Jump Drive Conservation')) {
      ls.setItem('Jump Drive Conservation', 4);
    }
    if (!ls.getItem('Jump Freighter')) {
      ls.setItem('Jump Freighter', 4);
    }
  }
  // Jump Options storage (rebuild menu components)
  function rebuildOptionsMenu() {
    var cynonet = ls.getItem('CynoNetNum');
    $('span.img-cyno-net').each(function() {
      cn = $(this).attr('cynonet');
      if (cn == cynonet)
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    });
    var ship = ls.getItem('Ship');
    if (!ship) {
      for (var s of knownShips) {
        $('#imgJumpShip'+s).addClass('hidden');
      }
      $('#imgJumpAnyShip').removeClass('hidden');
      $('#lbJumpShip').addClass('hidden');
    }
    else {
      for (var s of knownShips) {
        if (ship == s)
          $('#imgJumpShip'+s).removeClass('hidden');
        else
          $('#imgJumpShip'+s).addClass('hidden');
      }
      $('#imgJumpAnyShip').addClass('hidden');
      $('#lbJumpShip').html(ship);
      $('#lbJumpShip').removeClass('hidden');
    }
    var skill = ls.getItem('Jump Drive Calibration');
    $('#lbJumpCalibration').html(skill);
    for (var i = 1; i <= 5; i++) {
        if (skill == i)
          $('#imgJumpCalibration'+i.toString()).removeClass('hidden');
        else
          $('#imgJumpCalibration'+i.toString()).addClass('hidden');
    }
    skill = ls.getItem('Jump Drive Conservation');
    $('#lbJumpConservation').html(skill);
    for (var i = 1; i <= 5; i++) {
        if (skill == i)
          $('#imgJumpConservation'+i.toString()).removeClass('hidden');
        else
          $('#imgJumpConservation'+i.toString()).addClass('hidden');
    }
    skill = ls.getItem('Jump Freighter');
    $('#lbJumpFreighter').html(skill);
    for (var i = 1; i <= 5; i++) {
        if (skill == i)
          $('#imgJumpFreighter'+i.toString()).removeClass('hidden');
        else
          $('#imgJumpFreighter'+i.toString()).addClass('hidden');
    }
  }
  // Jump Options storage (rebuild panel links)
  function rebuildPanelLinks() {
    var ship = ls.getItem('Ship');
    if (!ship)
        ship = 'Rhea';
    var calibration_skill = parseInt(ls.getItem('Jump Drive Calibration'));
    var conservation_skill = parseInt(ls.getItem('Jump Drive Conservation'));
    var freighter_skill = parseInt(ls.getItem('Jump Freighter'));
    $('a.lnk-dtln').each(function() {
      cynonet = $(this).attr('cynonet');
      routes = $(this).attr('routes');
      var uri = 'https://evemaps.dotlan.net/jump/'+ship+','+calibration_skill+conservation_skill+freighter_skill+'/';
      for (var i = 1; i <= routes; i++) {
        if (i > 1) uri = uri + ':';
        uri = uri + $('#rowCynoRoute'+cynonet+'_'+i.toString()).attr('system');
      }
      $(this).attr('href', uri);
      $(this).html(uri);
    });
  }
  // Isotope Quantity Calculator
  function calcIsotope(lightyears, fuel_consumption, conservation_skill, freighter_skill) {
    return parseInt(lightyears * fuel_consumption * (1 - 0.1 * conservation_skill) * (1 - 0.1 * freighter_skill), 10);
  }
  // Jump Options storage (rebuild progress bar signals)
  function rebuildProgressBarSignals() {
    var ship = ls.getItem('Ship');
    //TODO:var calibration_skill = parseInt(ls.getItem('Jump Drive Calibration'));
    var conservation_skill = parseInt(ls.getItem('Jump Drive Conservation'));
    var freighter_skill = parseInt(ls.getItem('Jump Freighter'));
    for (var cn of contentsCynoNetwork) {
      cn_num = cn[0];
      for (var rt of cn[1]) {
        ly = rt[3];
        if (!ly) continue;
        signal = rt[2];
        if (signal == 'danger') continue;
        rt_num = rt[0];
        var nitrogen_used = calcIsotope(ly, 10000, conservation_skill, freighter_skill);
        var hydrogen_used = calcIsotope(ly, 8200, conservation_skill, freighter_skill);
        var oxygen_used = calcIsotope(ly, 9400, conservation_skill, freighter_skill);
        var helium_used = calcIsotope(ly, 8800, conservation_skill, freighter_skill);
        var nitrogen_times = parseInt(rt[4] / nitrogen_used, 10);
        var hydrogen_times = parseInt(rt[5] / hydrogen_used, 10);
        var oxygen_times = parseInt(rt[6] / oxygen_used, 10);
        var helium_times = parseInt(rt[7] / helium_used, 10);
        prgr = $('#prgrCynoRoute'+cn_num.toString()+'_'+rt_num.toString());
        if (prgr) {
          var times = 0;
          if (!ship) times = Math.min(nitrogen_times, hydrogen_times, oxygen_times, helium_times);
          else if (ship == 'Anshar') times = oxygen_times; // Gallente : Oxygen isotopes
          else if (ship == 'Ark') times = helium_times; // Amarr : Helium isotopes
          else if (ship == 'Nomad') times = hydrogen_times; // Minmatar : Hydrogen isotopes
          else if (ship == 'Rhea') times = nitrogen_times; // Caldari : Nitrogen isotopes
          if (signal == 'warning') {
            if (times >= 10) times = 2;
          }
          if (times < 2) {
            prgr.addClass('progress-bar-danger');
            prgr.removeClass('progress-bar-success');
            prgr.removeClass('progress-bar-warning');
          }
          else if (times >= 10) {
            prgr.addClass('progress-bar-success');
            prgr.removeClass('progress-bar-danger');
            prgr.removeClass('progress-bar-warning');
          }
          else {
            prgr.addClass('progress-bar-warning');
            prgr.removeClass('progress-bar-danger');
            prgr.removeClass('progress-bar-success');
          }
        }
      }
    }
  }
  // Jump Options storage (rebuild body components)
  function rebuildBody() {
    var ship = ls.getItem('Ship');
    //TODO:var calibration_skill = parseInt(ls.getItem('Jump Drive Calibration'));
    var conservation_skill = parseInt(ls.getItem('Jump Drive Conservation'));
    var freighter_skill = parseInt(ls.getItem('Jump Freighter'));
    $('tr.active td').each(function() {
      ly = $(this).attr('lightyears');
      if (ly) {
        ly = parseFloat(ly);
        var nitrogen_used = calcIsotope(ly, 10000, conservation_skill, freighter_skill);
        var hydrogen_used = calcIsotope(ly, 8200, conservation_skill, freighter_skill);
        var oxygen_used = calcIsotope(ly, 9400, conservation_skill, freighter_skill);
        var helium_used = calcIsotope(ly, 8800, conservation_skill, freighter_skill);
        cn_num = $(this).attr('cynonet');
        rt_num = $(this).attr('route');
        times = null
        contents = null
        for (var rt of contentsCynoNetwork[cn_num-1][1]) {
          if (rt[0] == rt_num) {
            contents = [rt[4],rt[5],rt[6],rt[7]]
            times = [parseInt(rt[4]/nitrogen_used), parseInt(rt[5]/hydrogen_used),
                     parseInt(rt[6]/oxygen_used), parseInt(rt[7]/helium_used)];
            break;
          }
        }
        $(this).html('Isotopes needed: <span class="nitrogen"><strong>' + nitrogen_used + '</strong> Ni</span> ' +
                      '<span class="hydrogen"><strong>' + hydrogen_used + '</strong> Hy</span> ' +
                      '<span class="oxygen"><strong>' + oxygen_used + '</strong> Ox</span> ' +
                      '<span class="helium"><strong>' + helium_used + '</strong> He</span>');
        if (times && contents) {
          if (contents[0])
            $('#niCynoRoute'+cn_num+'_'+rt_num).html('<abbr title="'+times[0]+' Rhea jumps">'+numLikeEve(contents[0])+'</abbr>');
          if (contents[1])
            $('#hyCynoRoute'+cn_num+'_'+rt_num).html('<abbr title="'+times[1]+' Nomad jumps">'+numLikeEve(contents[1])+'</abbr>');
          if (contents[2])
            $('#oxCynoRoute'+cn_num+'_'+rt_num).html('<abbr title="'+times[2]+' Anshar jumps">'+numLikeEve(contents[2])+'</abbr>');
          if (contents[3])
            $('#heCynoRoute'+cn_num+'_'+rt_num).html('<abbr title="'+times[3]+' Ark jumps">'+numLikeEve(contents[3])+'</abbr>');
        }
      }
    });
    if (!ship) { // show all
      for (var t of usedIsotopeTags) {
        $(t+'.nitrogen').removeClass('hidden');
        $(t+'.hydrogen').removeClass('hidden');
        $(t+'.oxygen').removeClass('hidden');
        $(t+'.helium').removeClass('hidden');
      }
    }
    else if (ship == 'Anshar') { // Gallente : Oxygen isotopes
      for (var t of usedIsotopeTags) {
        $(t+'.nitrogen').addClass('hidden');
        $(t+'.hydrogen').addClass('hidden');
        $(t+'.oxygen').removeClass('hidden');
        $(t+'.helium').addClass('hidden');
      }
    }
    else if (ship == 'Ark') { // Amarr : Helium isotopes
      for (var t of usedIsotopeTags) {
        $(t+'.nitrogen').addClass('hidden');
        $(t+'.hydrogen').addClass('hidden');
        $(t+'.oxygen').addClass('hidden');
        $(t+'.helium').removeClass('hidden');
      }
    }
    else if (ship == 'Nomad') { // Minmatar : Hydrogen isotopes
      for (var t of usedIsotopeTags) {
        $(t+'.nitrogen').addClass('hidden');
        $(t+'.hydrogen').removeClass('hidden');
        $(t+'.oxygen').addClass('hidden');
        $(t+'.helium').addClass('hidden');
      }
    }
    else if (ship == 'Rhea') { // Caldari : Nitrogen isotopes
      for (var t of usedIsotopeTags) {
        $(t+'.nitrogen').removeClass('hidden');
        $(t+'.hydrogen').addClass('hidden');
        $(t+'.oxygen').addClass('hidden');
        $(t+'.helium').addClass('hidden');
      }
    }
    var cynonet = ls.getItem('CynoNetNum');
    $('div.pn-cyno-net').each(function() {
      cn = $(this).attr('cynonet');
      if ((cynonet == 0) || (cynonet == cn.toString()))
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    })
  }

  // Jump Options menu and submenu setup
  $(document).ready(function(){
    $('.dropdown-submenu a.options-submenu').on("click", function(e){
      $(this).next('ul').toggle();
      e.stopPropagation();
      e.preventDefault();
    });
    $('a#btnCynoNetSel').on('click', function() {
      cynonet = $(this).attr('cynonet');
      ls.setItem('CynoNetNum', cynonet);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('a#btnJumpShip').on('click', function() {
      ship = $(this).attr('ship');
      ls.setItem('Ship', ship);
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    $('#btnJumpAnyShip').on('click', function() {
      ls.removeItem('Ship');
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    $('a#btnJumpCalibration').on('click', function() {
      skill = $(this).attr('skill');
      ls.setItem('Jump Drive Calibration', skill);
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    $('a#btnJumpConservation').on('click', function() {
      skill = $(this).attr('skill');
      ls.setItem('Jump Drive Conservation', skill);
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    $('a#btnJumpFreighter').on('click', function() {
      skill = $(this).attr('skill');
      ls.setItem('Jump Freighter', skill);
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    $('#btnResetOptions').on('click', function () {
      ls.clear();
      resetOptionsMenuToDefault();
      rebuildOptionsMenu();
      rebuildPanelLinks();
      rebuildProgressBarSignals();
      rebuildBody();
    });
    // first init
    resetOptionsMenuToDefault();
    rebuildOptionsMenu();
    rebuildPanelLinks();
    rebuildProgressBarSignals();
    rebuildBody();
  });
</script>""")


def dump_cynonetwork_into_report(ws_dir, sde_inv_positions, corp_cynonetwork):
    glf = open('{dir}/cynonetwork.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Cyno Network")
        __dump_corp_cynonetwork(glf, sde_inv_positions, corp_cynonetwork)
        __dump_footer(glf)
    finally:
        glf.close()


def __dump_market_groups_tree_nested(
        group_id,
        sde_market_groups,
        sde_icon_ids,
        market_groups_tree,
        market_data,
        market_data_printer):
    if not (str(group_id) in market_data) and not ("items" in market_groups_tree[str(group_id)]):
        return ""
    sde_group = sde_market_groups[str(group_id)]
    icon_id = sde_group["iconID"] if "iconID" in sde_group else 0
    tbl_glf = market_data_printer(group_id, market_data)
    sub_glf = ''
    if "items" in market_groups_tree[str(group_id)]:
        for group_id in market_groups_tree[str(group_id)]["items"]:
            sub_glf = sub_glf + __dump_market_groups_tree_nested(
                group_id,
                sde_market_groups,
                sde_icon_ids,
                market_groups_tree,
                market_data,
                market_data_printer
            )
    if not tbl_glf and not sub_glf:
        return ""
    glf = '' \
          '<div class="media">\n' \
          ' <div class="media-left media-top">{img}</div>\n' \
          ' <div class="media-body">\n' \
          '  <h4 class="media-heading">{nm}</h4>\n' \
          '{tbl}{sub}' \
          ' </div>\n' \
          '</div>\n'.format(
            img='<img class="media-object icn32" src="{src}">'.format(src=__get_icon_src(icon_id, sde_icon_ids)),
            nm=sde_group["nameID"]["en"],
            tbl=tbl_glf,
            sub=sub_glf
          )
    return glf


def __dump_market_groups_tree(glf, sde_market_groups, sde_icon_ids, market_groups_tree, market_data, market_data_printer):
    glf.write("""<ul class="media-list">
 <li class="media">""")

    if "roots" in market_groups_tree:
        roots = market_groups_tree["roots"]
        for group_id in roots:
            glf.write(
                __dump_market_groups_tree_nested(
                    group_id,
                    sde_market_groups,
                    sde_icon_ids,
                    market_groups_tree,
                    market_data,
                    market_data_printer)
            )

    glf.write(""" </li>
</ul>""")


def dump_bpos_into_report(
        ws_dir,
        sde_type_ids,
        sde_market_groups,
        sde_icon_ids,
        sde_bp_materials,
        corp_assets_data,
        corp_blueprints_data,
        market_groups_tree):
    market_data = {}
    for a in corp_assets_data:
        if not (str(a["type_id"]) in sde_bp_materials):
            continue
        if ("is_blueprint_copy" in a) and a["is_blueprint_copy"]:
            continue
        item_id = a["item_id"]
        blueprint = next((b for b in corp_blueprints_data if b["item_id"] == item_id), None)
        if blueprint is None:
            continue
        type_id = sde_type_ids[str(a["type_id"])]
        data_item = {
            "type_id": int(a["type_id"]),
            "name": type_id["name"]["en"],
            "me": blueprint["material_efficiency"],
            "te": blueprint["time_efficiency"],
            "quantity": 1
        }
        if "basePrice" in type_id:
            data_item["price"] = type_id["basePrice"]
        group_id = type_id["marketGroupID"]
        if not (str(group_id) in market_data):
            market_data[str(group_id)] = [data_item]
        else:
            prev_items = market_data[str(group_id)]
            found = False
            for prev in prev_items:
                if (prev["type_id"] == data_item["type_id"]) and (prev["me"] == data_item["me"])  and (prev["te"] == data_item["te"]):
                    prev["quantity"] = prev["quantity"] + 1
                    found = True
                    break
            if not found:
                market_data[str(group_id)].append(data_item)

    def blueprints_printer(group_id, market_data):
        if not (str(group_id) in market_data):
            return ""
        res = """<table class="table" style="width: unset; max-width: unset; margin-bottom: 0px;">
<thead>
 <tr>
 <th style="width:30px;">#</th>
 <th style="width:300px;">Blueprint</th>
 <th style="width:125px;">Base Price</th>
 <th style="width:85px;">Material Efficiency</th>
 <th style="width:85px;">Time Efficiency</th>
 <th style="width:75px;">Quantity</th>
 </tr>
</thead>
<tbody>
"""  # width: 700px
        items = market_data[str(group_id)]
        num = 1
        for item in items:
            res = res + '<tr>' \
                        '<th scope="row">{num}</th>' \
                        '<td>{nm}</td>' \
                        '<td>{prc}</td>' \
                        '<td>{me}</td>' \
                        '<td>{te}</td>' \
                        '<td>{q}</td>' \
                        '</tr>\n'.format(
                            num=num,
                            nm=item["name"],
                            prc='{:,.1f}'.format(item["price"]) if "price" in item else "",
                            me=item["me"],
                            te=item["te"],
                            q=item["quantity"]
                        )
            num = num + 1
        res = res + """</tbody>
</table>"""
        return res

    glf = open('{dir}/bpos.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "BPOs")
        glf.write("<div class='container-fluid'>\n")
        __dump_market_groups_tree(glf, sde_market_groups, sde_icon_ids, market_groups_tree, market_data, blueprints_printer)
        glf.write("</div>\n")
        __dump_footer(glf)
    finally:
        glf.close()


def __dump_corp_conveyor(
        glf,
        corp_bp_loc_data,
        corp_industry_jobs_data,
        corp_ass_names_data,
        corp_ass_loc_data,
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        stock_all_loc_ids,
        blueprint_loc_ids):
    glf.write("""
<nav class="navbar navbar-default">
 <div class="container-fluid">
  <div class="navbar-header">
   <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse" aria-expanded="false">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
   </button>
   <a class="navbar-brand" data-target="#"><span class="glyphicon glyphicon-tasks" aria-hidden="true"></span></a>
  </div>

  <div class="collapse navbar-collapse" id="bs-navbar-collapse">
   <ul class="nav navbar-nav">
    <li class="dropdown">
     <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Display Options <span class="caret"></span></a>
      <ul class="dropdown-menu">
       <li><a id="btnToggleActive" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowActive"></span> Show active blueprints</a></li>
       <li><a id="btnToggleMaterials" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowMaterials"></span> Show used materials</a></li>
       <li><a id="btnToggleLegend" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowLegend"></span> Show legend</a></li>
       <li role="separator" class="divider"></li>
       <li><a id="btnResetOptions" data-target="#" role="button">Reset options</a></li>
      </ul>
    </li>

    <li class="disabled"><a data-target="#" role="button">Problems</a></li>
   </ul>
   <form class="navbar-form navbar-right">
    <div class="form-group">
     <input type="text" class="form-control" placeholder="Item" disabled>
    </div>
    <button type="button" class="btn btn-default disabled">Search</button>
   </form>
  </div>
 </div>
</nav>
<div class="container-fluid">
""")

    __dump_corp_blueprints(
        glf,
        corp_bp_loc_data,
        corp_industry_jobs_data,
        corp_ass_names_data,
        corp_ass_loc_data,
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        stock_all_loc_ids,
        blueprint_loc_ids,
        enable_copy_to_clipboard=True)

    glf.write("""
<div id="legend-block">
 <hr>
 <h4>Legend</h4>
 <p>
  <span class="label label-default">copy</span>&nbsp;<span class="label label-success">2 4</span>&nbsp;<span
   class="badge">150</span> - blueprints <strong>copies</strong> with <strong>2</strong> material efficiency and
   <strong>4</strong> time efficiency with total of <strong>150</strong> runs.
 </p>
 <p>
  <span class="label label-info">original</span>&nbsp;<span class="label label-success">10 20</span>&nbsp;<span
   class="badge">2</span>&nbsp;<span class="label label-info">active</span> - <strong>two</strong>
   <strong>original</strong> blueprints with <strong>10</strong> material efficiency and <strong>20</strong> time efficiency,
   production is currently <strong>active</strong>.
 </p>
 <p>
""")
    glf.write('<span style="white-space:nowrap"><img class="icn24" src="{src}"> 30 x Ice Harvester I </span>'
              '&nbsp;<span class="label label-warning"><img class="icn24" src="{src}"> 6 x Ice Harvester I </span>&nbsp;-'
              '&nbsp;<strong>30</strong> items used in the production, the items are missing <strong>6</strong>.'.
              format(src=__get_img_src(16278, 32)))
    glf.write("""
 </p>
</div>
</div>
<script>
  // Conveyor Options storage (prepare)
  ls = window.localStorage;

  // Conveyor Options storage (init)
  function resetOptionsMenuToDefault() {
    if (!ls.getItem('Show Legend')) {
      ls.setItem('Show Legend', 1);
    }
    if (!ls.getItem('Show Active')) {
      ls.setItem('Show Active', 1);
    }
    if (!ls.getItem('Show Materials')) {
      ls.setItem('Show Materials', 1);
    }
  }
  // Conveyor Options storage (rebuild menu components)
  function rebuildOptionsMenu() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#imgShowLegend').removeClass('hidden');
    else
      $('#imgShowLegend').addClass('hidden');
    show = ls.getItem('Show Active');
    if (show == 1)
      $('#imgShowActive').removeClass('hidden');
    else
      $('#imgShowActive').addClass('hidden');
    show = ls.getItem('Show Materials');
    if (show == 1)
      $('#imgShowMaterials').removeClass('hidden');
    else
      $('#imgShowMaterials').addClass('hidden');
  }
  // Conveyor Options storage (rebuild body components)
  function rebuildBody() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#legend-block').removeClass('hidden');
    else
      $('#legend-block').addClass('hidden');
    show = ls.getItem('Show Active');
    $('span.qind-blueprints-active').each(function() {
      if (show == 1)
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    })
    show = ls.getItem('Show Materials');
    $('div.qind-materials-used').each(function() {
      if (show == 1)
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    })
  }
  // Conveyor Options menu and submenu setup
  $(document).ready(function(){
    $('#btnToggleLegend').on('click', function () {
      show = (ls.getItem('Show Legend') == 1) ? 0 : 1;
      ls.setItem('Show Legend', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnToggleActive').on('click', function () {
      show = (ls.getItem('Show Active') == 1) ? 0 : 1;
      ls.setItem('Show Active', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnToggleMaterials').on('click', function () {
      show = (ls.getItem('Show Materials') == 1) ? 0 : 1;
      ls.setItem('Show Materials', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnResetOptions').on('click', function () {
      ls.clear();
      resetOptionsMenuToDefault();
      rebuildOptionsMenu();
      rebuildBody();
    });
    // first init
    resetOptionsMenuToDefault();
    rebuildOptionsMenu();
    rebuildBody();
    // Working with clipboard
    $('a.qind-copy-btn').each(function() {
      $(this).tooltip();
    })
    $('a.qind-copy-btn').bind('click', function () {
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val($(this).attr('data-copy')).select();
      try {
        success = document.execCommand("copy");
        if (success) {
          $(this).trigger('copied', ['Copied!']);
        }
      } finally {
        $temp.remove();
      }
    });
    $('a.qind-copy-btn').bind('copied', function(event, message) {
      $(this).attr('title', message)
        .tooltip('fixTitle')
        .tooltip('show')
        .attr('title', "Copy to clipboard")
        .tooltip('fixTitle');
    });
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
      // какой-то код ...
      $('a.qind-copy-btn').each(function() {
        $(this).addClass('hidden');
      })
    }
  });
</script>
""")


__g_pattern_c2s1 = re.compile(r'(.)([A-Z][a-z]+)')
__g_pattern_c2s2 = re.compile(r'([a-z0-9])([A-Z])')


def __camel_to_snake(name):  # https://stackoverflow.com/a/1176023
  name = __g_pattern_c2s1.sub(r'\1_\2', name)
  return __g_pattern_c2s2.sub(r'\1_\2', name).lower()


def dump_conveyor_into_report(
        ws_dir,
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        corp_industry_jobs_data,
        corp_ass_names_data,
        corp_ass_loc_data,
        corp_bp_loc_data,
        stock_all_loc_ids,
        blueprint_loc_ids):
    glf = open('{dir}/conveyor.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Conveyor")
        __dump_corp_conveyor(glf, corp_bp_loc_data, corp_industry_jobs_data, corp_ass_names_data, corp_ass_loc_data, sde_type_ids, sde_bp_materials, sde_market_groups, stock_all_loc_ids, blueprint_loc_ids)
        #__dump_corp_assets(glf, corp_ass_loc_data, corp_ass_names_data, sde_type_ids)
        __dump_footer(glf)
    finally:
        glf.close()


def __dump_corp_accounting_nested_tbl(
        glf,
        loc_id,
        loc_dict,
        sde_type_ids,
        filter_flags):
    h3_and_table_printed = False
    if "items" in loc_dict:
        __itms_keys = loc_dict["items"].keys()
        for __loc_id in __itms_keys:
            itm_dict = loc_dict["items"][str(__loc_id)]
            # отбрасываем элементы не по фильтру (например нет списка "delivery")
            __filter_found = filter_flags is None
            if not __filter_found:
                for __filter in filter_flags:
                    if __filter in itm_dict["flags"]:
                        __filter_found = True
                        break
            if not __filter_found:
                continue
            # пишем заголовок таблицы (название системы)
            if not h3_and_table_printed:
                h3_and_table_printed = True
                __loc_name = loc_dict["loc_name"]
                if __loc_name is None:
                    __loc_name = loc_id
                glf.write(
                    '<h3>{where}</strong><!--{id}--></h3>\n'.
                    format(where='{} '.format(__loc_name) if not (__loc_name is None) else "",
                           id=loc_id))
                glf.write("""
<div class="table-responsive">
  <table class="table table-condensed">
<thead>
 <tr>
  <th style="width:40px;">#</th>
  <th>Items</th>
  <th style="text-align: right;">Cost, ISK</th>
  <th style="text-align: right;">Volume, m&sup3;</th>
 </tr>
</thead>
<tbody>
""")
            # получаем данные по текущему справочнику
            loc_name = itm_dict["loc_name"]
            foreign = itm_dict["foreign"]
            forbidden = itm_dict["forbidden"] if "forbidden" in itm_dict else False
            type_id = itm_dict["type_id"]
            if loc_name is None:
                loc_name = loc_id
            glf.write(
                '<tr><td colspan="4">'
                '<div class="media">'
                ' <div class="media-left">{img}</div>'
                ' <div class="media-body"><strong>{where}</strong>{what}{foreign}{forbidden}<!--{id}--></div>'
                '</div>'
                '</td></tr>\n'.
                format(where='{} '.format(loc_name) if not (loc_name is None) else "",
                       id=__loc_id,
                       foreign='&nbsp;<small><span class="label label-warning">foreign</span></small>' if foreign else "",
                       forbidden='&nbsp;<small><span class="label label-danger">forbidden</span></small>' if forbidden else "",
                       img='<img class="media-object icn32" src="{src}">'.format(src=__get_img_src(type_id, 32)) if not (type_id is None) else "",
                       what='&nbsp;<small>{}</small> '.format(get_item_name_by_type_id(sde_type_ids, type_id)) if not (type_id is None) else ""))
            row_id = 1
            if "flags" in itm_dict:
                __f_keys = itm_dict["flags"].keys()
                for __flag in __f_keys:  # "CorpDeliveries"
                    # отбрасываем элементы не по фильтру (например нет списка "delivery")
                    __filter_found = filter_flags is None
                    if not __filter_found and (0 != filter_flags.count(__flag)):
                        __filter_found = True
                    if not __filter_found:
                        continue
                    # выводим информацию по содержимому location (группы товаров)
                    __flag_dict = itm_dict["flags"][str(__flag)]
                    __g_keys = __flag_dict.keys()
                    for __group_id in __g_keys:
                        __group_dict = __flag_dict[str(__group_id)]
                        glf.write('<tr{color}>'
                                  ' <th scope="row">{num}</th>\n'
                                  ' <td>{nm}{tag}</td>'
                                  ' <td align="right">{cost:,.1f}</td>'
                                  ' <td align="right">{volume:,.1f}</td>'
                                  '</tr>'.
                                  format(num=row_id,
                                         nm=__group_dict["group"],
                                         cost=__group_dict["cost"],
                                         volume=__group_dict["volume"],
                                         tag='' if not (filter_flags is None) and (len(filter_flags) == 1) else
                                             '&nbsp;<small><span class="label label-default">{flag}</span></small>'.
                                             format(flag=__camel_to_snake(str(__flag))),
                                         color=' style="color:green;"' if __flag == "BlueprintsReactions" else ""))
                        row_id = row_id + 1
    if h3_and_table_printed:
        glf.write("""
</tbody>
 </table>
</div>
""")


def __dump_corp_accounting_details(
        glf,
        __key,
        corporation_name,
        corporation_id,
        __corp_tree,
        sde_type_ids):
    __dump_any_into_modal_header(
        glf,
        '<span class="text-primary">{nm}</span> {key}'.format(nm=corporation_name,
                                                              key="" if __key is None else __key),
        '{nm}_{key}'.format(nm=corporation_id,
                            key="all" if __key is None else __key),
        "btn-xs",
        "details&hellip;")
    __roots = __corp_tree.keys()
    __filter = None if __key is None else [__key]
    for root in __roots:
        __dump_corp_accounting_nested(
            glf,
            root,
            __corp_tree[str(root)],
            sde_type_ids,
            __filter)  # ["CorpDeliveries"]
    __dump_any_into_modal_footer(glf)


def __dump_corp_accounting_nested(
        glf,
        root_id,
        root,
        sde_type_ids,
        filter_flags):
    if "region" in root:
        __filter_found = filter_flags is None
        if not __filter_found:
            for __filter in filter_flags:
                if ("flags" in root) and (root["flags"].count(__filter) > 0):
                    __filter_found = True
                    break
        if not __filter_found:
            return
        glf.write('<h2>{rgn}<!--{id}--></h2>\n'.format(rgn=root["region"], id=root_id))
        __sys_keys = root["systems"].keys()
        for loc_id in __sys_keys:
            system = root["systems"][str(loc_id)]
            __dump_corp_accounting_nested_tbl(glf, loc_id, system, sde_type_ids, filter_flags)
    else:
        glf.write('<h2>???</h2>\n')
        __dump_corp_accounting_nested_tbl(glf, root_id, root, sde_type_ids, filter_flags)


def __dump_corp_accounting(
        glf,
        sde_type_ids,
        corps_accounting):
    glf.write("""
    <nav class="navbar navbar-default">
     <div class="container-fluid">
      <div class="navbar-header">
       <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
       </button>
       <a class="navbar-brand" data-target="#"><span class="glyphicon glyphicon-list-alt" aria-hidden="true"></span></a>
      </div>

      <div class="collapse navbar-collapse" id="bs-navbar-collapse">
       <ul class="nav navbar-nav">
        <li class="dropdown">
         <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Display Options <span class="caret"></span></a>
          <ul class="dropdown-menu">
           <li><a id="btnToggleBlueprints" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowBlueprints"></span> Show blueprints and reactions</a></li>
           <li><a id="btnToggleLegend" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowLegend"></span> Show legend</a></li>
           <li role="separator" class="divider"></li>
           <li><a id="btnResetOptions" data-target="#" role="button">Reset options</a></li>
          </ul>
        </li>

        <li class="disabled"><a data-target="#" role="button">Problems</a></li>
       </ul>
       <form class="navbar-form navbar-right">
        <div class="form-group">
         <input type="text" class="form-control" placeholder="Item" disabled>
        </div>
        <button type="button" class="btn btn-default disabled">Search</button>
       </form>
      </div>
     </div>
    </nav>
    <div class="container-fluid">
    """)
    glf.write("""
<div class="table-responsive">
  <table class="table table-condensed table-hover">
<thead>
 <tr>
  <th style="width:40px;">#</th>
  <th>Locations</th>
  <th style="text-align: right;">Cost, ISK</th>
  <th style="text-align: right;">Volume, m&sup3;</th>
  <th style="text-align: center;">Details</th>
 </tr>
</thead>
<tbody>
""")

    __corp_keys = corps_accounting.keys()
    for corporation_id in __corp_keys:
        __corp = corps_accounting[str(corporation_id)]
        glf.write('<tr class="active">'
                  ' <td colspan="5"><span class="text-primary"><strong>{nm}</strong></span></td>'
                  '</tr>\n'.
                  format(nm=__corp["corporation"]))
        row_num = 1
        __summary_cost = 0
        __summary_volume = 0
        __stat_keys = __corp["stat"].keys()
        for __key in __stat_keys:
            __stat_dict = __corp["stat"][str(__key)]
            if ("omit_in_summary" in __stat_dict) and __stat_dict["omit_in_summary"]:
                continue
            glf.write('<tr>'
                      ' <th scope="row">{num}</th>\n'
                      ' <td>{nm}</td>'
                      ' <td align="right">{cost:,.1f}</td>'
                      ' <td align="right">{volume:,.1f}</td>'
                      ' <td align="center">'.
                      format(num=row_num,
                             nm=__key,  # "CorpDeliveries"
                             cost=__stat_dict["cost"],
                             volume=__stat_dict["volume"]))
            # подсчёт общей статистики
            __summary_cost = __summary_cost + __stat_dict["cost"]
            __summary_volume = __summary_volume + __stat_dict["volume"]
            # добавление details на страницу
            __dump_corp_accounting_details(
                glf,
                __key,
                __corp["corporation"],
                corporation_id,
                __corp["tree"],
                sde_type_ids)
            glf.write('</td>'
                      '</tr>\n')
            row_num = row_num + 1
        __copy2clpbrd = '&nbsp;<a data-target="#" role="button" data-copy="{cost:.1f}" class="qind-copy-btn"' \
                        '  data-toggle="tooltip"><span class="glyphicon glyphicon-copy"' \
                        '  aria-hidden="true"></span></a>'. \
                        format(cost=__summary_cost)
        glf.write('<tr>'
                  ' <th></th>\n'
                  ' <td><strong>Summary</strong></td>\n'
                  ' <td align="right"><strong>{cost:,.1f}{clbrd}</strong></td>'
                  ' <td align="right"><strong>{volume:,.1f}</strong></td>'
                  ' <td align="center">'.
                  format(cost=__summary_cost,
                         volume=__summary_volume,
                         clbrd=__copy2clpbrd))
        # добавление details в summary
        __dump_corp_accounting_details(
            glf,
            None,
            __corp["corporation"],
            corporation_id,
            __corp["tree"],
            sde_type_ids)
        glf.write('</td>'
                  '</tr>\n')
        # добавление в подвал (под summary) информацию об omitted-категориях (такая у нас Blueprints & Reactions)
        # повторно запускаем цикл
        for __key in __stat_keys:
            __stat_dict = __corp["stat"][str(__key)]
            if not ("omit_in_summary" in __stat_dict) or not __stat_dict["omit_in_summary"]:
                continue
            glf.write('<tr class="qind-blueprints-stat">'
                      ' <th></th>\n'
                      ' <td style="color:green;">{nm}</td>'
                      ' <td style="color:green;" align="right">{cost:,.1f}</td>'
                      ' <td style="color:green;" align="right">{volume:,.1f}</td>'
                      ' <td align="center">'.
                      format(nm=__key,  # "BlueprintsReactions"
                             cost=__stat_dict["cost"],
                             volume=__stat_dict["volume"]))
            # добавление details на страницу
            __dump_corp_accounting_details(
                glf,
                __key,
                __corp["corporation"],
                corporation_id,
                __corp["tree"],
                sde_type_ids)
            glf.write('</td>'
                      '</tr>\n')

    glf.write("""
</tbody>
 </table>
</div>
""")
    glf.write("""
<div id="legend-block">
 <hr>
 <h4>Legend</h4>
 <p>
  <small><span class="label label-warning">foreign</span></small> - the station or structure is owned by another corporation.
 </p>
 <p>
  <small><span class="label label-danger">forbidden</span></small> - now there is no access to the station or structure.
 </p>
 <p>
  <small><span class="label label-default">corp_deliveries</span>, <span class="label label-default">office_folder</span>,&hellip;</small> - locations of items.
 </p>
""")
    glf.write("""
</div>
<script>
  // Accounting Options storage (prepare)
  ls = window.localStorage;

  // Accounting Options storage (init)
  function resetOptionsMenuToDefault() {
    if (!ls.getItem('Show Legend')) {
      ls.setItem('Show Legend', 1);
    }
    if (!ls.getItem('Show Blueprints')) {
      ls.setItem('Show Blueprints', 1);
    }
  }
  // Accounting Options storage (rebuild menu components)
  function rebuildOptionsMenu() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#imgShowLegend').removeClass('hidden');
    else
      $('#imgShowLegend').addClass('hidden');
    show = ls.getItem('Show Blueprints');
    if (show == 1)
      $('#imgShowBlueprints').removeClass('hidden');
    else
      $('#imgShowBlueprints').addClass('hidden');
  }
  // Accounting Options storage (rebuild body components)
  function rebuildBody() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#legend-block').removeClass('hidden');
    else
      $('#legend-block').addClass('hidden');
    show = ls.getItem('Show Blueprints');
    $('tr.qind-blueprints-stat').each(function() {
      if (show == 1)
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    })
  }
  // Accounting Options menu and submenu setup
  $(document).ready(function(){
    $('#btnToggleLegend').on('click', function () {
      show = (ls.getItem('Show Legend') == 1) ? 0 : 1;
      ls.setItem('Show Legend', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnToggleBlueprints').on('click', function () {
      show = (ls.getItem('Show Blueprints') == 1) ? 0 : 1;
      ls.setItem('Show Blueprints', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnResetOptions').on('click', function () {
      ls.clear();
      resetOptionsMenuToDefault();
      rebuildOptionsMenu();
      rebuildBody();
    });
    // first init
    resetOptionsMenuToDefault();
    rebuildOptionsMenu();
    rebuildBody();
    // Working with clipboard
    $('a.qind-copy-btn').each(function() {
      $(this).tooltip();
    })
    $('a.qind-copy-btn').bind('click', function () {
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val($(this).attr('data-copy')).select();
      try {
        success = document.execCommand("copy");
        if (success) {
          $(this).trigger('copied', ['Copied!']);
        }
      } finally {
        $temp.remove();
      }
    });
    $('a.qind-copy-btn').bind('copied', function(event, message) {
      $(this).attr('title', message)
        .tooltip('fixTitle')
        .tooltip('show')
        .attr('title', "Copy to clipboard")
        .tooltip('fixTitle');
    });
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
      // какой-то код ...
      $('a.qind-copy-btn').each(function() {
        $(this).addClass('hidden');
      })
    }
  });
</script>
""")


def dump_accounting_into_report(
        ws_dir,
        sde_type_ids,
        corps_accounting):
    glf = open('{dir}/accounting.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Accounting")
        __dump_corp_accounting(glf, sde_type_ids, corps_accounting)
        __dump_footer(glf)
    finally:
        glf.close()


def __dump_corp_blueprints_tbl(
        glf,
        corps_blueprints):
    glf.write("""
<nav class="navbar navbar-default">
 <div class="container-fluid">
  <div class="navbar-header">
   <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-navbar-collapse" aria-expanded="false">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
   </button>
   <a class="navbar-brand" data-target="#"><span class="glyphicon glyphicon-duplicate" aria-hidden="true"></span></a>
  </div>

  <div class="collapse navbar-collapse" id="bs-navbar-collapse">
   <ul class="nav navbar-nav">
    <li class="dropdown">
     <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Display Options <span class="caret"></span></a>
      <ul class="dropdown-menu">
       <li><a id="btnTogglePriceTags" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowPriceTags"></span> Show price tags</a></li>
       <li><a id="btnToggleWithStatuses" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowWithStatuses"></span> Show only industry jobs</a></li>
       <li><a id="btnToggleLegend" data-target="#" role="button"><span class="glyphicon glyphicon-star" aria-hidden="true" id="imgShowLegend"></span> Show legend</a></li>
       <li role="separator" class="divider"></li>
       <li><a id="btnResetOptions" data-target="#" role="button">Reset options</a></li>
      </ul>
    </li>

    <li class="disabled"><a data-target="#" role="button">Problems</a></li>
   </ul>
   <form class="navbar-form navbar-right">
    <div class="form-group">
     <input type="text" class="form-control" placeholder="Item" disabled>
    </div>
    <button type="button" class="btn btn-default disabled">Search</button>
   </form>
  </div>
 </div>
</nav>
<div class="container-fluid">
""")
    __corp_keys = corps_blueprints.keys()
    for corporation_id in __corp_keys:
        __corp = corps_blueprints[str(corporation_id)]
        glf.write('<div class="panel panel-primary">\n'
                  ' <div class="panel-heading"><h3 class="panel-title">{nm}</h3></div>\n'.
                  format(nm=__corp["corporation"]))
        glf.write("""
<div class="panel-body">
 <div class="table-responsive">
  <table class="table table-condensed table-hover">
<thead>
 <tr>
  <th>#</th>
  <th>Blueprint</th>
  <th>ME</th>
  <th>TE</th>
  <th>Qty</th>
  <th>Price, ISK</th>
  <th>Location</th>
 </tr>
</thead>
<tbody>
""")
        row_num = 1
        __summary_cost = 0
        for __blueprint_dict in __corp["blueprints"]:
            # выясняем сколько стоит один чертёж?
            __price = ""
            if "average_price" in __blueprint_dict:
                __price = '{cost:,.1f} <sup class="qind-price-tag"><span class="label label-primary">A</span></sup>'.format(cost=__blueprint_dict["average_price"])
            elif "adjusted_price" in __blueprint_dict:
                __price = '{cost:,.1f} <sup class="qind-price-tag"><span class="label label-info">J</span></sup>'.format(cost=__blueprint_dict["adjusted_price"])
            elif "base_price" in __blueprint_dict:
                __price = '{cost:,.1f} <sup class="qind-price-tag"><span class="label label-default">B</span></sup>'.format(cost=__blueprint_dict["base_price"])
            # проверяем работки по текущему чертежу?
            __status = ""
            if "st" in __blueprint_dict:  # [ active, cancelled, delivered, paused, ready, reverted ]
                __blueprint_status = __blueprint_dict["st"]
                if (__blueprint_status == "active") or (__blueprint_status == "delivered"):
                    __status = '&nbsp;<span class="label label-info">{}</span>'.format(__blueprint_status)
                elif __blueprint_status == "ready":
                    __status = '&nbsp;<span class="label label-success">{}</span>'.format(__blueprint_status)
                elif (__blueprint_status == "cancelled") or (__blueprint_status == "paused") or (__blueprint_status == "reverted"):
                    __status = '&nbsp;<span class="label label-warning">{}</span>'.format(__blueprint_status)
                else:
                    __status = '&nbsp;<span class="label label-danger">{}</span>'.format(__blueprint_status)
            # вывод в таблицу информацию о чертеже
            glf.write('<tr class="{qind_cl}">'
                      ' <th scope="row">{num}</th>\n'
                      ' <td>{nm}{st}</td>'
                      ' <td>{me}</td>'
                      ' <td>{te}</td>'
                      ' <td>{q}</td>'
                      ' <td align="right">{price}</td>'
                      ' <td><small>{loc}</small></td>'
                      '</tr>\n'.
                      format(num=row_num,
                             nm=__blueprint_dict["name"],
                             st=__status,
                             qind_cl="qind-bp-nonjob" if not __status else "qind-bp-job",
                             me=__blueprint_dict["me"],
                             te=__blueprint_dict["te"],
                             q=__blueprint_dict["q"],
                             price=__price,
                             loc=__blueprint_dict["loc"]))
            # подсчёт общей статистики
            # __summary_cost = __summary_cost + __stat_dict["cost"]
            row_num = row_num + 1
        glf.write("""
</tbody>
   </table>
  </div>
 </div>
</div>
""")

    glf.write("""
<div id="legend-block">
 <hr>
 <h4>Legend</h4>
 <p>
  <span class="label label-primary">A</span>, <span class="label label-info">J</span>, <span class="label label-default">B</span> - <strong>price tags</strong>
  to indicate type of market' price. There are <span class="label label-primary">A</span> average price (<i>current market price</i>),
  and <span class="label label-info">J</span> adjusted price (<i>average over the last 28 days</i>) and <span class="label label-default">B</span>
  base price (<i>standart CCP item price</i>).
 </p>
 <p>
  <span class="label label-info">active</span>, <span class="label label-info">delivered</span>,
  <span class="label label-success">ready</span>, <span class="label label-warning">cancelled</span>,
  <span class="label label-warning">paused</span>, <span class="label label-warning">reverted</span> - all possible
  <strong>statuses</strong> of blueprints that are in industry mode.
 </p>
</div>

<script>
  // Accounting Options storage (prepare)
  ls = window.localStorage;

  // Accounting Options storage (init)
  function resetOptionsMenuToDefault() {
    if (!ls.getItem('Show Legend')) {
      ls.setItem('Show Legend', 1);
    }
    if (!ls.getItem('Show Price Tags')) {
      ls.setItem('Show Price Tags', 1);
    }
    if (!ls.getItem('Show With Statuses')) {
      ls.setItem('Show With Statuses', 0);
    }
  }
  // Accounting Options storage (rebuild menu components)
  function rebuildOptionsMenu() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#imgShowLegend').removeClass('hidden');
    else
      $('#imgShowLegend').addClass('hidden');
    show = ls.getItem('Show Price Tags');
    if (show == 1)
      $('#imgShowPriceTags').removeClass('hidden');
    else
      $('#imgShowPriceTags').addClass('hidden');
    show = ls.getItem('Show With Statuses');
    if (show == 1)
      $('#imgShowWithStatuses').removeClass('hidden');
    else
      $('#imgShowWithStatuses').addClass('hidden');
  }
  // Accounting Options storage (rebuild body components)
  function rebuildBody() {
    show = ls.getItem('Show Legend');
    if (show == 1)
      $('#legend-block').removeClass('hidden');
    else
      $('#legend-block').addClass('hidden');
    show = ls.getItem('Show Price Tags');
    $('sup.qind-price-tag').each(function() {
      if (show == 1)
        $(this).removeClass('hidden');
      else
        $(this).addClass('hidden');
    })
    show = ls.getItem('Show With Statuses');
    $('tr.qind-bp-nonjob').each(function() {
      if (show == 1)
        $(this).addClass('hidden');
      else
        $(this).removeClass('hidden');
    })
  }
  // Accounting Options menu and submenu setup
  $(document).ready(function(){
    $('#btnToggleLegend').on('click', function () {
      show = (ls.getItem('Show Legend') == 1) ? 0 : 1;
      ls.setItem('Show Legend', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnTogglePriceTags').on('click', function () {
      show = (ls.getItem('Show Price Tags') == 1) ? 0 : 1;
      ls.setItem('Show Price Tags', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnToggleWithStatuses').on('click', function () {
      show = (ls.getItem('Show With Statuses') == 1) ? 0 : 1;
      ls.setItem('Show With Statuses', show);
      rebuildOptionsMenu();
      rebuildBody();
    });
    $('#btnResetOptions').on('click', function () {
      ls.clear();
      resetOptionsMenuToDefault();
      rebuildOptionsMenu();
      rebuildBody();
    });
    // first init
    resetOptionsMenuToDefault();
    rebuildOptionsMenu();
    rebuildBody();
    // Working with clipboard
    $('a.qind-copy-btn').each(function() {
      $(this).tooltip();
    })
    $('a.qind-copy-btn').bind('click', function () {
      var $temp = $("<input>");
      $("body").append($temp);
      $temp.val($(this).attr('data-copy')).select();
      try {
        success = document.execCommand("copy");
        if (success) {
          $(this).trigger('copied', ['Copied!']);
        }
      } finally {
        $temp.remove();
      }
    });
    $('a.qind-copy-btn').bind('copied', function(event, message) {
      $(this).attr('title', message)
        .tooltip('fixTitle')
        .tooltip('show')
        .attr('title', "Copy to clipboard")
        .tooltip('fixTitle');
    });
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
      // какой-то код ...
      $('a.qind-copy-btn').each(function() {
        $(this).addClass('hidden');
      })
    }
  });
</script>
""")


def dump_blueprints_into_report(
        ws_dir,
        corps_blueprints):
    glf = open('{dir}/blueprints.html'.format(dir=ws_dir), "wt+", encoding='utf8')
    try:
        __dump_header(glf, "Blueprints")
        __dump_corp_blueprints_tbl(glf, corps_blueprints)
        __dump_footer(glf)
    finally:
        glf.close()
