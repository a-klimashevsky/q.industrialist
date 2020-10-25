﻿""" Q.Industry (desktop/mobile)

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

>>> python eve_sde_tools.py
>>> python q_industry.py --pilot="Qandra Si" --online --cache_dir=~/.q_industrialist

Requires application scopes:
    * esi-industry.read_corporation_jobs.v1 - Requires role(s): Factory_Manager

"""
import sys

import eve_esi_interface as esi
import postgresql_interface as db

import q_industrialist_settings
import eve_sde_tools
import console_app
import render_html_industry

from __init__ import __version__


g_module_default_settings = {
    # either "station_id" or "station_name" is required
    # if "station_id" is unknown, then the names of stations and structures will be
    # additionally loaded (too slow, please identify and set "station_id")
    "factory:station_id": 60003760,
    "factory:station_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
    # hangar, which stores blueprint copies to build T2 modules
    "factory:blueprints_hangars": [1]
}


def __get_db_connection():
    qidb = db.QIndustrialistDatabase("workflow", debug=True)
    qidb.connect(q_industrialist_settings.g_database)
    return qidb


def main():
    qidb = __get_db_connection()
    module_settings = qidb.load_module_settings(g_module_default_settings)
    db_monthly_jobs = qidb.select_all_rows(
        "SELECT wmj_id,wmj_active,wmj_quantity,wmj_eft,wmj_remarks "
        "FROM workflow_monthly_jobs;")
    db_factory_containers = qidb.select_all_rows(
        "SELECT wfc_id,wfc_name,wfc_active,wfc_disabled "
        "FROM workflow_factory_containers;")

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

    sde_type_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "typeIDs")

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

    # Requires role(s): Factory_Manager
    corp_industry_jobs_data = interface.get_esi_paged_data(
        "corporations/{}/industry/jobs/".format(corporation_id))
    print("\n'{}' corporation has {} industry jobs".format(corporation_name, len(corp_industry_jobs_data)))
    sys.stdout.flush()

    # сохраняем данные по производству в БД
    wij = db.QWorkflowIndustryJobs(qidb)
    new_jobs_found = wij.actualize(corp_industry_jobs_data)
    print("\n'{}' corporation has {} new jobs since last update".format(corporation_name, new_jobs_found))
    sys.stdout.flush()
    del wij

    # выбираем накопленные данные по производству из БД
    workflow_industry_jobs = qidb.select_all_rows(
        "SELECT"
        " wij_product_tid AS ptid,"
        " sum(wij_cost) AS cost,"
        " sum(wij_runs) AS runs,"
        " wij_bp_tid AS bptid,"
        " wij_bp_lid AS bplid,"
        " wij_out_lid AS olid,"
        " wij_facility_id AS fid "
        "FROM workflow_industry_jobs "
        "WHERE wij_activity_id=1 "
        "GROUP BY 1,4,5,6,7 "
        "ORDER BY 1;")
    db_workflow_industry_jobs = [{"ptid": wij[0], "cost": wij[1], "runs": wij[2], "bptid": wij[3], "bplid": wij[4], "olid": wij[5], "fid": wij[6]} for wij in workflow_industry_jobs]
    del workflow_industry_jobs

    print("\nBuilding report...")
    sys.stdout.flush()

    render_html_industry.dump_industry_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        db_workflow_industry_jobs
    )

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    del qidb
    print("\nDone")


if __name__ == "__main__":
    main()