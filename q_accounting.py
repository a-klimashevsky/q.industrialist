﻿""" Q.Accounting (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

>>> python eve_sde_tools.py --cache_dir=~/.q_industrialist
>>> python q_accounting.py --pilot1="Qandra Si" --pilot2="Your Name" --online --cache_dir=~/.q_industrialist

Required application scopes:
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
    * esi-universe.read_structures.v1 - Requires: access token
    * esi-wallet.read_corporation_wallets.v1 - Requires one of: Accountant, Junior_Accountant
"""
import json
import sys
import requests

import console_app
import eve_esi_interface as esi
import eve_esi_tools
import eve_sde_tools
import q_industrialist_settings
import render_html_accounting

from __init__ import __version__


def __build_accounting_append(
        __type_id,
        __quantity,
        __group_id,
        __group_name,
        __group_icon,
        eve_market_prices_data,
        sde_type_ids,
        __cas1_stat_flag,
        __ca5_station_flag,
        skip_certain_groups,
        process_only_specified_groups,
        prefer_base_price,
        do_not_use_any_price,
        top_level_hangar):
    if not (skip_certain_groups is None):
        if __group_id in skip_certain_groups:  # напр. Blueprints & Reactions (пропускаем)
            return
    if not (process_only_specified_groups is None):
        if not (__group_id in process_only_specified_groups):  # напр. Blueprints & Reactions (обрабатываем)
            return
    __hangar_num = None if top_level_hangar is None else int(top_level_hangar)
    __ca5_key = str(__group_id) if __hangar_num is None else '{}_{}'.format(__group_id, __hangar_num)
    if not (__ca5_key in __ca5_station_flag):
        __ca5_station_flag.update({__ca5_key: {
            "hangar_num": __hangar_num,
            # "group_id": __group_id,
            "group": __group_name,
            "icon": __group_icon,
            "volume": 0,
            "cost": 0
        }})
    __ca6_hangar_group = __ca5_station_flag[__ca5_key]  # верим в лучшее, данные по маркету тут должны быть...
    __type_dict = sde_type_ids[str(__type_id)]
    if "volume" in __type_dict:
        __sum = __type_dict["volume"] * __quantity
        __ca6_hangar_group["volume"] += __sum
        __cas1_stat_flag["volume"] += __sum
    if not do_not_use_any_price:
        __price = None
        if prefer_base_price and ("basePrice" in __type_dict):
            __price = __type_dict["basePrice"]
        if __price is None:
            __price_dict = next((p for p in eve_market_prices_data if p['type_id'] == int(__type_id)), None)
            if not (__price_dict is None):
                if "average_price" in __price_dict:
                    __price = __price_dict["average_price"]
                elif "adjusted_price" in __price_dict:
                    __price = __price_dict["adjusted_price"]
                elif "basePrice" in __type_dict:
                    __price = __type_dict["basePrice"]
            elif "basePrice" in __type_dict:
                __price = __type_dict["basePrice"]
        if not (__price is None):
            __sum = __price * __quantity
            __ca6_hangar_group["cost"] += __sum
            __cas1_stat_flag["cost"] += __sum


def __build_accounting_nested(
        itm_id,
        sde_type_ids,
        sde_market_groups,
        eve_market_prices_data,
        corp_assets_tree,
        corp_assets_data,
        __cas1_stat_flag,
        __ca5_station_flag,
        skip_certain_groups,
        process_only_specified_groups,
        top_level_hangar):
    __tree_dict = corp_assets_tree[str(itm_id)]
    __item_dict = corp_assets_data[int(__tree_dict["index"])]
    __type_id = int(__item_dict["type_id"])
    __quantity = int(__item_dict["quantity"])
    # __location_flag = __item_dict["location_flag"]
    __group_id = eve_sde_tools.get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, __type_id)
    # номер ангара добывается на первом и сохраняется на всех последующих уровнях вложенности
    if top_level_hangar is None:
        if __item_dict["location_flag"][:-1] == "CorpSAG":
            top_level_hangar = int(__item_dict["location_flag"][-1:])
    if not (__group_id is None):
        __build_accounting_append(
            __type_id,
            __quantity,
            __group_id,
            sde_market_groups[str(__group_id)]["nameID"]["en"],
            sde_market_groups[str(__group_id)]["iconID"] if "iconID" in sde_market_groups[str(__group_id)] else None,
            eve_market_prices_data,
            sde_type_ids,
            __cas1_stat_flag,
            __ca5_station_flag,
            skip_certain_groups,
            process_only_specified_groups,
            False,
            False,
            top_level_hangar)
    if str(itm_id) in corp_assets_tree:
        __cat1 = corp_assets_tree[str(itm_id)]
        if "items" in __cat1:
            for __itm_id in __cat1["items"]:
                __build_accounting_nested(
                    __itm_id,
                    sde_type_ids,
                    sde_market_groups,
                    eve_market_prices_data,
                    corp_assets_tree,
                    corp_assets_data,
                    __cas1_stat_flag,
                    __ca5_station_flag,
                    skip_certain_groups,
                    process_only_specified_groups,
                    top_level_hangar)
    return


def __build_accounting_register_flag(
        __location_flag,
        __ca1_region,
        __ca3_station,
        corp_accounting_stat):
    if __ca1_region["flags"].count(__location_flag) == 0:
        __ca1_region["flags"].append(__location_flag)
    __ca4_station_flags = __ca3_station["flags"]
    if not (__location_flag in __ca4_station_flags):
        __ca4_station_flags.update({__location_flag: {}})
    __ca5_station_flag = __ca4_station_flags[__location_flag]
    if not (__location_flag in corp_accounting_stat):
        corp_accounting_stat.update({__location_flag: {"volume": 0, "cost": 0}})
    __cas1_stat_flag = corp_accounting_stat[__location_flag]
    return __ca5_station_flag, __cas1_stat_flag


def __build_accounting_register_region(
        region_id,
        region_name,
        loc_id,
        loc_name,
        corp_accounting_tree):
    if not (str(region_id) in corp_accounting_tree):
        corp_accounting_tree.update({str(region_id): {"region": region_name, "systems": {}, "flags": []}})
    __ca1_region = corp_accounting_tree[str(region_id)]
    __ca1_region["systems"].update({str(loc_id): {"loc_name": loc_name, "items": {}}})
    __ca2_system = __ca1_region["systems"][str(loc_id)]
    return __ca1_region, __ca2_system


def __build_accounting_station(
        loc_id,
        corp_assets_data,
        corp_accounting_stat,
        corp_assets_tree,
        sde_type_ids,
        sde_market_groups,
        eve_market_prices_data,
        __ca1_region,
        __ca3_station,
        skip_certain_groups,
        process_only_specified_groups):
    __tree = corp_assets_tree[str(loc_id)]
    __tree_items = corp_assets_tree[str(loc_id)]["items"] if "items" in __tree else None
    if not (__tree_items is None):
        for a in __tree_items:
            __item_id = int(a)
            __tree_dict = corp_assets_tree[str(__item_id)]
            __item_dict = corp_assets_data[int(__tree_dict["index"])]
            if __item_dict["type_id"] == 16159:  # EVE Alliance (пропускаем, бесполезная инфа, есть есть только в профиле СЕО)
                continue
            __location_flag = __item_dict["location_flag"]  # CorpDeliveries, OfficeFolder
            __ca5_station_flag, __cas1_stat_flag = __build_accounting_register_flag(
                __location_flag,
                __ca1_region,
                __ca3_station,
                corp_accounting_stat)
            __build_accounting_nested(
                __item_id,
                sde_type_ids,
                sde_market_groups,
                eve_market_prices_data,
                corp_assets_tree,
                corp_assets_data,
                __cas1_stat_flag,
                __ca5_station_flag,
                skip_certain_groups,
                process_only_specified_groups,
                None)  # корпоративный ангар всегда вложен в OfficeFolder и находится уровнем ниже


def __build_accounting_blueprints_nested(
        __item_id,
        sde_type_ids,
        sde_market_groups,
        eve_market_prices_data,
        corp_assets_tree,
        corp_assets_data,
        corp_accounting_stat,
        __ca1_region,
        __ca3_station):
    __ca5_station_flag = __cas1_stat_flag = None
    __tree_dict = corp_assets_tree[str(__item_id)]
    __item_dict = corp_assets_data[int(__tree_dict["index"])]
    __type_id = int(__item_dict["type_id"])
    __quantity = int(__item_dict["quantity"])
    # __location_flag = __item_dict["location_flag"]
    __group_id = eve_sde_tools.get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, __type_id)
    if not (__group_id is None) and (__group_id == 2):  # Blueprints and Reactions (добавляем только этот тип)
        # регистрируем регион и станцию, на которой обнаружены blueprint
        if __ca5_station_flag is None:
            __location_flag = "BlueprintsReactions"
            __ca5_station_flag, __cas1_stat_flag = __build_accounting_register_flag(
                __location_flag,
                __ca1_region,
                __ca3_station,
                corp_accounting_stat)
            __cas1_stat_flag.update({"omit_in_summary": True})
        # определяем, является ли чертёж БПО или БПЦ? (для БПО предпочтительная цена : base_price, для БПЦ : average_price и adjusted_price)
        __is_blueprint_copy = ("is_blueprint_copy" in __item_dict) and bool(__item_dict["is_blueprint_copy"])
        __build_accounting_append(
            __type_id,
            __quantity,
            __group_id,
            sde_market_groups[str(__group_id)]["nameID"]["en"],
            sde_market_groups[str(__group_id)]["iconID"] if "iconID" in sde_market_groups[str(__group_id)] else None,
            eve_market_prices_data,
            sde_type_ids,
            __cas1_stat_flag,
            __ca5_station_flag,
            None,  # в статистику попадают все группы, но следующий фильтр ограничит...
            [2],   # ...обработку только Blueprints and Reactions
            not __is_blueprint_copy,  # признак использования base_price
            __is_blueprint_copy,  # поправка: для БПЦ-чертежей любая цена от ЦЦП невалидна
            None)  #TODO: номер ангара
    if str(__item_id) in corp_assets_tree:
        __cat1 = corp_assets_tree[str(__item_id)]
        if "items" in __cat1:
            for __nested_item_id in __cat1["items"]:
                __build_accounting_blueprints_nested(
                    __nested_item_id,
                    sde_type_ids,
                    sde_market_groups,
                    eve_market_prices_data,
                    corp_assets_tree,
                    corp_assets_data,
                    corp_accounting_stat,
                    __ca1_region,
                    __ca3_station)


def __build_accounting_blueprints(
        loc_id,
        corp_assets_data,
        corp_accounting_stat,
        corp_assets_tree,
        sde_type_ids,
        sde_market_groups,
        eve_market_prices_data,
        __ca1_region,
        __ca3_station):
    # на текущей станции получаем все item-ы и собираем сводную статистику по Blueprints & Reactions
    __tree = corp_assets_tree[str(loc_id)]
    __tree_items = corp_assets_tree[str(loc_id)]["items"] if "items" in __tree else None
    if __tree_items is None:
        return
    for a in __tree_items:
        __item_id = int(a)
        __build_accounting_blueprints_nested(
            __item_id,
            sde_type_ids,
            sde_market_groups,
            eve_market_prices_data,
            corp_assets_tree,
            corp_assets_data,
            corp_accounting_stat,
            __ca1_region,
            __ca3_station)


def __build_accounting(
        sde_type_ids,
        sde_inv_names,
        sde_inv_items,
        sde_market_groups,
        eve_market_prices_data,
        corp_ass_names_data,
        foreign_structures_data,
        foreign_structures_forbidden_ids,
        corp_assets_tree,
        corp_assets_data):
    if not ("roots" in corp_assets_tree):
        return None
    corp_accounting_stat = {}
    corp_accounting_tree = {}
    __roots = corp_assets_tree["roots"]
    for loc_id in __roots:
        region_id, region_name, loc_name, __dummy0 = eve_esi_tools.get_assets_location_name(
            loc_id,
            sde_inv_names,
            sde_inv_items,
            corp_ass_names_data,
            foreign_structures_data)
        if not (region_id is None):
            __ca1_region, __ca2_system = __build_accounting_register_region(
                region_id,
                region_name,
                loc_id,
                loc_name,
                corp_accounting_tree)
            for itm in corp_assets_tree[str(loc_id)]["items"]:
                __itm = str(itm)
                __ca2_system["items"].update({__itm: {"type_id": corp_assets_tree[__itm]["type_id"]}})
                __dummy1, __dummy2, loc_name, foreign = eve_esi_tools.get_assets_location_name(
                    itm,
                    sde_inv_names,
                    sde_inv_items,
                    corp_ass_names_data,
                    foreign_structures_data)
                __ca3_station = __ca2_system["items"][__itm]
                __ca3_station.update({"loc_name": loc_name, "foreign": foreign, "flags": {}})
                # имущество собственных станций и таможек тоже учитываем в сводной статистике
                if not foreign:
                    __tree_dict = corp_assets_tree[str(itm)] if str(itm) in corp_assets_tree else None
                    __item_dict = corp_assets_data[int(__tree_dict["index"])] if "index" in __tree_dict else None
                    if not (__item_dict is None):  # может попастся NPC-станция, пропускаем, это точно не наше имущество
                        __location_flag = __item_dict["location_flag"]
                        if __location_flag == "AutoFit":
                            __ca5_station_flag, __cas1_stat_flag = __build_accounting_register_flag(
                                __location_flag,
                                __ca1_region,
                                __ca3_station,
                                corp_accounting_stat)
                            __type_id = int(__item_dict["type_id"])
                            __group_id = eve_sde_tools.get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, __type_id)
                            if not (__group_id is None):
                                __build_accounting_append(
                                    __type_id,
                                    1,
                                    __group_id,
                                    sde_market_groups[str(__group_id)]["nameID"]["en"],
                                    sde_market_groups[str(__group_id)]["iconID"] if "iconID" in sde_market_groups[str(__group_id)] else None,
                                    eve_market_prices_data,
                                    sde_type_ids,
                                    __cas1_stat_flag,
                                    __ca5_station_flag,
                                    [2],  # пропускаем: Blueprints and Reactions (собирается в отдельную группу)
                                    None, # Обрабатываем все остальные типы и группы имущества
                                    False,
                                    False,
                                    None)  #TODO: а какой тут номер ангара?
                # на текущей станции получаем все location_flag и собираем сводную статистику по каждой группе
                __build_accounting_station(
                    itm,
                    corp_assets_data,
                    corp_accounting_stat,
                    corp_assets_tree,
                    sde_type_ids,
                    sde_market_groups,
                    eve_market_prices_data,
                    __ca1_region,
                    __ca3_station,
                    [2],  # пропускаем: Blueprints and Reactions (собирается в отдельную группу)
                    None)  # Обрабатываем все остальные типы и группы имущества
                # с Blueprints & Reactions работаем индивидуально! (добавляем их в отдельную виртуальную группу)
                __build_accounting_blueprints(
                    itm,
                    corp_assets_data,
                    corp_accounting_stat,
                    corp_assets_tree,
                    sde_type_ids,
                    sde_market_groups,
                    eve_market_prices_data,
                    __ca1_region,
                    __ca3_station)
        else:
            # не удалось получить сведения о регионе, - это неспроста, скорее всего на эту стуктуру у корпы forbidden
            __region_id = None
            if int(loc_id) in foreign_structures_forbidden_ids:
                __region_id = 0  # "(none)"
                __ca1_region, __ca2_system = __build_accounting_register_region(
                    __region_id,
                    "Forbidden",
                    0,
                    "(no data)",
                    corp_accounting_tree)
                __ca2_system["items"].update({str(loc_id): {"type_id": None}})
                __ca3_station = __ca2_system["items"][str(loc_id)]
                __ca3_station.update({"loc_name": str(loc_id), "foreign": True, "forbidden": True, "flags": {}})
            else:
                __region_id = 3006  # "Unknown"
                __ca1_region, __ca2_system = __build_accounting_register_region(
                    __region_id,
                    "Unknown",
                    0,
                    "(no data)",
                    corp_accounting_tree)
                __ca2_system["items"].update({str(loc_id): {"type_id": None}})
                __ca3_station = __ca2_system["items"][str(loc_id)]
                __ca3_station.update({"loc_name": str(loc_id), "foreign": True, "flags": {}})
            # на текущей станции получаем все location_flag и собираем сводную статистику по каждой группе
            __build_accounting_station(
                loc_id,
                corp_assets_data,
                corp_accounting_stat,
                corp_assets_tree,
                sde_type_ids,
                sde_market_groups,
                eve_market_prices_data,
                __ca1_region,
                __ca3_station,
                [2],  # пропускаем: Blueprints and Reactions (собирается в отдельную группу)
                None)  # Обрабатываем все остальные типы и группы имущества
            # возможная ситуация - в список попал, но не добавился EVE Alliance маркер, который есть только у СЕО
            if len(__ca1_region["flags"]) == 0:
                del corp_accounting_tree[str(__region_id)]
    return corp_accounting_stat, corp_accounting_tree


def __build_wallets_stat(corp_wallet_journal_data):
    corp_wallet_stat = [{}, {}, {}, {}, {}, {}, {}]
    for wallet_division_jounal in enumerate(corp_wallet_journal_data):
        __wallet_dict = corp_wallet_stat[wallet_division_jounal[0]]
        for w in wallet_division_jounal[1]:
            # https://github.com/esi/eve-glue/blob/master/eve_glue/wallet_journal_ref.py
            __ref_type = str(w.get("ref_type"))  # mandatory
            __amount = w.get("amount", None)  # optional
            if not (__ref_type in __wallet_dict):
                __wallet_dict.update({__ref_type: 0.00})
            __wallet_dict[__ref_type] += __amount
    return corp_wallet_stat


def main():
    # работа с параметрами командной строки, получение настроек запуска программы, как то: работа в offline-режиме,
    # имя пилота ранее зарегистрированного и для которого имеется аутентификационный токен, регистрация нового и т.д.
    argv_prms = console_app.get_argv_prms()

    sde_type_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "typeIDs")
    sde_inv_names = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invNames")
    sde_inv_items = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invItems")
    sde_market_groups = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "marketGroups")
    sde_icon_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "iconIDs")

    """
    === Сведения по рассчёту цены ===
    
    Данные из .yaml:
    36:
     basePrice: 32.0
     groupID: 18
     iconID: 401
     marketGroupID: 1857
     name:
      en: Mexallon
     portionSize: 1
     published: true
     volume: 0.01
    ---
    Данные из https://esi.evetech.net/ui/#/Market/get_markets_prices :
    {
     "adjusted_price": 44.1,
     "average_price": 92.64,
     "type_id": 36
    }
    ---
    Ситуация на рынке https://image.prntscr.com/image/0Oqy5FlqRniAstG2wvSd7A.png :
    Sell: 85 ISK
    Buy: 88.64 ISK
    ----
    Текущая стоимость, которую показывает Евка https://image.prntscr.com/image/-8liCZ8TRHWIaSpZ6Kzhew.png :
    92.6 ISK
    ---
    Полезная информация https://www.reddit.com/r/Eve/comments/5zegqw/how_does_ccp_calculate_averageadjusted_price/ :
    adjusted_price - средняя за 28 дней
    """

    corps_accounting = {}
    eve_market_prices_data = None
    for pilot_name in argv_prms["character_names"]:
        # настройка Eve Online ESI Swagger interface
        auth = esi.EveESIAuth(
            '{}/auth_cache'.format(argv_prms["workspace_cache_files_dir"]),
            debug=True)
        client = esi.EveESIClient(
            auth,
            debug=False,
            logger=True,
            user_agent='Q.Industrialist v{ver}'.format(ver=__version__))
        interface = esi.EveOnlineInterface(
            client,
            q_industrialist_settings.g_client_scope,
            cache_dir='{}/esi_cache'.format(argv_prms["workspace_cache_files_dir"]),
            offline_mode=argv_prms["offline_mode"])

        authz = interface.authenticate(pilot_name)
        character_id = authz["character_id"]
        character_name = authz["character_name"]

        # Public information about a character
        character_data = interface.get_esi_data(
            "characters/{}/".format(character_id))
        # Public information about a corporation
        corporation_data = interface.get_esi_data(
            "corporations/{}/".format(character_data["corporation_id"]))

        corporation_id = character_data["corporation_id"]
        corporation_name = corporation_data["name"]
        print("\n{} is from '{}' corporation".format(character_name, corporation_name))
        sys.stdout.flush()

        if eve_market_prices_data is None:
            # Public information about market prices
            eve_market_prices_data = interface.get_esi_data("markets/prices/")
            print("\nEVE market has {} prices".format(len(eve_market_prices_data)))
            sys.stdout.flush()

        # Requires role(s): Director
        corp_wallets_data = interface.get_esi_paged_data(
            "corporations/{}/wallets/".format(corporation_id))
        print("\n'{}' corporation has {} wallet divisions".format(corporation_name, len(corp_wallets_data)))
        sys.stdout.flush()

        # Requires role(s): Accountant, Junior_Accountant
        corp_wallet_journal_data = [None, None, None, None, None, None, None]
        for w in corp_wallets_data:
            division = w["division"]
            corp_wallet_journal_data[division-1] = interface.get_esi_paged_data(
                "corporations/{}/wallets/{}/journal/".format(corporation_id, division))
            print("'{}' corporation has {} wallet#{} transactions\n".format(corporation_name, len(corp_wallet_journal_data[division-1]), division))
            sys.stdout.flush()

        # Requires role(s): Director
        corp_assets_data = interface.get_esi_paged_data(
            "corporations/{}/assets/".format(corporation_id))
        print("\n'{}' corporation has {} assets".format(corporation_name, len(corp_assets_data)))
        sys.stdout.flush()

        # Получение названий контейнеров, станций, и т.п. - всё что переименовывается ingame
        corp_ass_names_data = []
        corp_ass_named_ids = eve_esi_tools.get_assets_named_ids(corp_assets_data)
        if len(corp_ass_named_ids) > 0:
            # Requires role(s): Director
            corp_ass_names_data = interface.get_esi_data(
                "corporations/{}/assets/names/".format(corporation_id),
                json.dumps(corp_ass_named_ids, indent=0, sort_keys=False))
        print("\n'{}' corporation has {} custom asset's names".format(corporation_name, len(corp_ass_names_data)))
        sys.stdout.flush()

        # Поиск тех станций, которые не принадлежат корпорации (на них имеется офис, но самой станции в ассетах нет)
        foreign_structures_data = {}
        foreign_structures_ids = eve_esi_tools.get_foreign_structures_ids(corp_assets_data)
        foreign_structures_forbidden_ids = []
        if len(foreign_structures_ids) > 0:
            # Requires: access token
            for structure_id in foreign_structures_ids:
                try:
                    universe_structure_data = interface.get_esi_data(
                        "universe/structures/{}/".format(structure_id))
                    foreign_structures_data.update({str(structure_id): universe_structure_data})
                except requests.exceptions.HTTPError as err:
                    status_code = err.response.status_code
                    if status_code == 403:  # это нормально, что часть структур со временем могут оказаться Forbidden
                        foreign_structures_forbidden_ids.append(structure_id)
                    else:
                        raise
                except:
                    print(sys.exc_info())
                    raise
        print("\n'{}' corporation has offices in {} foreign stations".format(corporation_name, len(foreign_structures_data)))
        if len(foreign_structures_forbidden_ids) > 0:
            print("\n'{}' corporation has offices in {} forbidden stations : {}".format(corporation_name, len(foreign_structures_forbidden_ids), foreign_structures_forbidden_ids))
        sys.stdout.flush()

        # Построение дерева ассетов, с узлави в роли станций и систем, и листьями в роли хранящихся
        # элементов, в виде:
        # { location1: {items:[item1,item2,...],type_id,location_id},
        #   location2: {items:[item3],type_id} }
        corp_assets_tree = eve_esi_tools.get_assets_tree(corp_assets_data, foreign_structures_data, sde_inv_items, virtual_hierarchy_by_corpsag=False)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_assets_tree.{}".format(corporation_name), corp_assets_tree)

        # Построение дерева имущества (сводная информация, учитывающая объёмы и ориентировочную стоимость asset-ов)
        print("\nBuilding {} accounting tree and stat...".format(corporation_name))
        sys.stdout.flush()
        corp_accounting_stat, corp_accounting_tree = __build_accounting(
            sde_type_ids,
            sde_inv_names,
            sde_inv_items,
            sde_market_groups,
            eve_market_prices_data,
            corp_ass_names_data,
            foreign_structures_data,
            foreign_structures_forbidden_ids,
            corp_assets_tree,
            corp_assets_data)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_accounting_stat.{}".format(corporation_name), corp_accounting_stat)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_accounting_tree.{}".format(corporation_name), corp_accounting_tree)
        corp_wallet_stat = __build_wallets_stat(corp_wallet_journal_data)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_wallet_stat.{}".format(corporation_name), corp_wallet_stat)

        corps_accounting.update({str(corporation_id): {
            "corporation": corporation_name,
            "wallet": corp_wallets_data,
            "wallet_stat": corp_wallet_stat,
            "stat": corp_accounting_stat,
            "tree": corp_accounting_tree
        }})

    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corps_accounting", corps_accounting)

    # Построение дерева asset-ов:
    print("\nBuilding accounting report...")
    sys.stdout.flush()
    render_html_accounting.dump_accounting_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        sde_icon_ids,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        corps_accounting)

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    main()
