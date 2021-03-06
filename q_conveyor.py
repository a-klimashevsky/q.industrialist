﻿""" Q.Conveyor (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Copy q_conveyor_settings.py.template into q_conveyor_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

>>> python eve_sde_tools.py --cache_dir=~/.q_industrialist
>>> python q_conveyor.py --pilot="Qandra Si" --online --cache_dir=~/.q_industrialist

Requires application scopes:
    * esi-industry.read_corporation_jobs.v1 - Requires role(s): Factory_Manager
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
    * esi-corporations.read_blueprints.v1 - Requires role(s): Director
"""
import sys
import json
import requests
import re

import eve_esi_interface as esi

import eve_esi_tools
import eve_sde_tools
import console_app
import render_html_conveyor
import q_industrialist_settings
import q_conveyor_settings

from __init__ import __version__


def main():
    # работа с параметрами командной строки, получение настроек запуска программы, как то: работа в offline-режиме,
    # имя пилота ранее зарегистрированного и для которого имеется аутентификационный токен, регистрация нового и т.д.
    argv_prms = console_app.get_argv_prms()

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

    authz = interface.authenticate(argv_prms["character_names"][0])
    character_id = authz["character_id"]
    character_name = authz["character_name"]

    # Public information about a character
    character_data = interface.get_esi_data(
        "characters/{}/".format(character_id),
        fully_trust_cache=True)
    # Public information about a corporation
    corporation_data = interface.get_esi_data(
        "corporations/{}/".format(character_data["corporation_id"]),
        fully_trust_cache=True)

    corporation_id = character_data["corporation_id"]
    corporation_name = corporation_data["name"]
    print("\n{} is from '{}' corporation".format(character_name, corporation_name))
    sys.stdout.flush()

    sde_type_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "typeIDs")
    sde_inv_names = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invNames")
    sde_inv_items = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invItems")
    sde_market_groups = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "marketGroups")
    sde_bp_materials = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "blueprints")
    sde_icon_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "iconIDs")

    # Построение списка модулей и ресурсов, которые используются в производстве
    materials_for_bps = eve_sde_tools.get_materials_for_blueprints(sde_bp_materials)
    research_materials_for_bps = eve_sde_tools.get_research_materials_for_blueprints(sde_bp_materials)

    # Requires role(s): Director
    corp_assets_data = interface.get_esi_paged_data(
        "corporations/{}/assets/".format(corporation_id))
    print("\n'{}' corporation has {} assets".format(corporation_name, len(corp_assets_data)))
    sys.stdout.flush()

    # Requires role(s): Director
    corp_blueprints_data = interface.get_esi_paged_data(
        "corporations/{}/blueprints/".format(corporation_id))
    print("\n'{}' corporation has {} blueprints".format(corporation_name, len(corp_blueprints_data)))
    sys.stdout.flush()

    # Requires role(s): Factory_Manager
    corp_industry_jobs_data = interface.get_esi_paged_data(
        "corporations/{}/industry/jobs/".format(corporation_id))
    print("\n'{}' corporation has {} industry jobs".format(corporation_name, len(corp_industry_jobs_data)))
    sys.stdout.flush()

    corp_ass_names_data = []
    corp_ass_named_ids = eve_esi_tools.get_assets_named_ids(corp_assets_data)
    if len(corp_ass_named_ids) > 0:
        # Requires role(s): Director
        corp_ass_names_data = interface.get_esi_data(
            "corporations/{}/assets/names/".format(corporation_id),
            json.dumps(corp_ass_named_ids, indent=0, sort_keys=False))
    print("\n'{}' corporation has {} custom asset's names".format(corporation_name, len(corp_ass_names_data)))
    sys.stdout.flush()

    # Построение иерархических списков БПО и БПЦ, хранящихся в корпоративных ангарах
    corp_bp_loc_data = eve_esi_tools.get_corp_bp_loc_data(corp_blueprints_data, corp_industry_jobs_data)
    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_bp_loc_data", corp_bp_loc_data)

    # Построение списка модулей и ресуров, которые имеются в распоряжении корпорации и
    # которые предназначены для использования в чертежах
    corp_ass_loc_data = eve_esi_tools.get_corp_ass_loc_data(corp_assets_data, containers_filter=None)
    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_ass_loc_data", corp_ass_loc_data)

    # Поиск тех станций, которые не принадлежат корпорации (на них имеется офис, но самой станции в ассетах нет)
    foreign_structures_data = {}
    foreign_structures_ids = eve_esi_tools.get_foreign_structures_ids(corp_assets_data)
    foreign_structures_forbidden_ids = []
    if len(foreign_structures_ids) > 0:
        # Requires: access token
        for structure_id in foreign_structures_ids:
            try:
                universe_structure_data = interface.get_esi_data(
                    "universe/structures/{}/".format(structure_id),
                    fully_trust_cache=True)
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
    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_assets_tree", corp_assets_tree)

    # Поиск контейнеров, которые участвуют в производстве
    conveyour_entities = []
    for __manuf_dict in enumerate(q_conveyor_settings.g_manufacturing):
        # находим контейнеры по заданным названиям
        blueprint_loc_ids = []
        for tmplt in __manuf_dict[1]["conveyor_container_names"]:
            blueprint_loc_ids.extend([n["item_id"] for n in corp_ass_names_data if re.search(tmplt, n['name'])])
        # кешируем признак того, что контейнеры являются стоком материалов
        same_stock_container = ("same_stock_container" in __manuf_dict[1]) and bool(__manuf_dict[1]["same_stock_container"])
        fixed_number_of_runs = __manuf_dict[1]["fixed_number_of_runs"] if "fixed_number_of_runs" in __manuf_dict[1] else None
        # находим станцию, где расположены найденные контейнеры
        for id in blueprint_loc_ids:
            __loc_dict = eve_esi_tools.get_universe_location_by_item(
                id,
                sde_inv_names,
                sde_inv_items,
                corp_assets_tree,
                corp_ass_names_data,
                foreign_structures_data
            )
            if not ("station_id" in __loc_dict):
                continue
            __station_id = __loc_dict["station_id"]
            __conveyor_entity = next((id for id in conveyour_entities if id["station_id"] == __station_id), None)
            if __conveyor_entity is None:
                __conveyor_entity = __loc_dict
                __conveyor_entity.update({"containers": [], "stock": [], "exclude": []})
                conveyour_entities.append(__conveyor_entity)
                # на этой же станции находим контейнер со стоком материалов
                if same_stock_container:
                    __conveyor_entity["stock"].append({"id": id, "name": next((n["name"] for n in corp_ass_names_data if n['item_id'] == id), None)})
                else:
                    for tmplt in __manuf_dict[1]["stock_container_names"]:
                        __stock_ids = [n["item_id"] for n in corp_ass_names_data if re.search(tmplt, n['name'])]
                        for __stock_id in __stock_ids:
                            __stock_loc_dict = eve_esi_tools.get_universe_location_by_item(
                                __stock_id,
                                sde_inv_names,
                                sde_inv_items,
                                corp_assets_tree,
                                corp_ass_names_data,
                                foreign_structures_data
                            )
                            if ("station_id" in __stock_loc_dict) and (__station_id == __stock_loc_dict["station_id"]):
                                __conveyor_entity["stock"].append({"id": __stock_id, "name": next((n["name"] for n in corp_ass_names_data if n['item_id'] == __stock_id), None)})
                # на этой же станции находим контейнеры, из которых нельзя доставать чертежи для производства материалов
                for tmplt in __manuf_dict[1]["exclude_container_names"]:
                    __exclude_ids = [n["item_id"] for n in corp_ass_names_data if re.search(tmplt, n['name'])]
                    for __exclude_id in __exclude_ids:
                        __stock_loc_dict = eve_esi_tools.get_universe_location_by_item(
                            __exclude_id,
                            sde_inv_names,
                            sde_inv_items,
                            corp_assets_tree,
                            corp_ass_names_data,
                            foreign_structures_data
                        )
                        if ("station_id" in __stock_loc_dict) and (__station_id == __stock_loc_dict["station_id"]):
                            __conveyor_entity["exclude"].append({"id": __exclude_id, "name": next((n["name"] for n in corp_ass_names_data if n['item_id'] == __exclude_id), None)})
            # добавляем к текущей станции контейнер с чертежами
            # добаляем в свойства контейнера фиксированное кол-во запусков чертежей из настроек
            __conveyor_entity["containers"].append({
                "id": id,
                "name": next((n["name"] for n in corp_ass_names_data if n['item_id'] == id), None),
                "fixed_number_of_runs": fixed_number_of_runs})

    # перечисляем станции и контейнеры, которые были найдены
    print('\nFound conveyor containters and station ids...')
    for ce in conveyour_entities:
        print('  {} = {}'.format(ce["station_id"], ce["station"]))
        for cec in ce["containers"]:
            print('    {} = {}'.format(cec["id"], cec["name"]))
        for ces in ce["stock"]:
            print('    {} = {}'.format(ces["id"], ces["name"]))
        for cee in ce["exclude"]:
            print('    {} = {}'.format(cee["id"], cee["name"]))
    sys.stdout.flush()

    print("\nBuilding report...")
    sys.stdout.flush()

    render_html_conveyor.dump_conveyor_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # настройки генерации отчёта
        conveyour_entities,
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        sde_bp_materials,
        sde_market_groups,
        sde_icon_ids,
        # esi данные, загруженные с серверов CCP
        corp_industry_jobs_data,
        corp_ass_names_data,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        corp_ass_loc_data,
        corp_bp_loc_data,
        corp_assets_tree,
        materials_for_bps,
        research_materials_for_bps)

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    main()
