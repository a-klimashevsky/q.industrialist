﻿""" Console application tools and utils
"""
import sys
import getopt
from pathlib import Path

from __init__ import __version__


def get_argv_prms():
    # работа с параметрами командной строки, получение настроек запуска программы, как то: работа в offline-режиме,
    # имя пилота ранее зарегистрированного и для которого имеется аутентификационный токен, регистрация нового и т.д.
    res = {
        "character_names": [],
        "signup_new_character": False,
        "offline_mode": False,
        "workspace_cache_files_dir": '{}/.q_industrialist'.format(str(Path.home()))
    }
    exit_or_wrong_getopt = None
    print_version_only = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "version", "pilot=", "signup", "offline", "online",
                                                        "cache_dir=", "pilot1=", "pilot2=", "pilot3="])
    except getopt.GetoptError:
        exit_or_wrong_getopt = 2
    if exit_or_wrong_getopt is None:
        for opt, arg in opts:  # noqa
            if opt in ('-h', "--help"):
                exit_or_wrong_getopt = 0
                break
            elif opt in ('-v', "--version"):
                exit_or_wrong_getopt = 0
                print_version_only = True
                break
            elif opt in ("--pilot", "--pilot1", "--pilot2", "--pilot3"):
                res["character_names"].append(arg)
            elif opt in ("--signup"):
                res["signup_new_character"] = True
            elif opt in ("--offline"):
                res["offline_mode"] = True
            elif opt in ("--online"):
                res["offline_mode"] = False
            elif opt in ("--cache_dir"):
                res["workspace_cache_files_dir"] = arg[:-1] if arg[-1:] == '/' else arg
        # д.б. либо указано имя, либо флаг регистрации нового пилота
        if (len(res["character_names"]) == 0) == (res["signup_new_character"] == False):
            exit_or_wrong_getopt = 0
    if not (exit_or_wrong_getopt is None):
        print('q.industrialist {ver} - (c) 2020 qandra.si@gmail.com\n'
              'Released under the GNU GPL.\n'.format(ver=__version__))
        if print_version_only:
            sys.exit(exit_or_wrong_getopt)
        print('\n'
              '-h --help                   Print this help screen\n'
              '   --pilot=NAME             Character name previously signed in\n'
              '   --pilot1=NAME            1st character name previously signed in\n'
              '   --pilot2=NAME            2nd character name previously signed in\n'
              '   --pilot3=NAME            3rd character name previously signed in\n'
              '   --signup                 Signup new character\n'
              '   --offline                Flag which says that we are working offline\n'
              '   --online                 Flag which says that we are working online (default)\n'
              '   --cache_dir=PATH         Directory where esi/auth cache files stored\n'
              '-v --version                Print version info\n'
              '\n'
              'Usage: {app} --pilot="Qandra Si" --offline --cache_dir=/tmp\n'.
            format(app=sys.argv[0]))
        sys.exit(exit_or_wrong_getopt)

    return res
