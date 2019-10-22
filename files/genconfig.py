#!/usr/bin/env python

"""Overrides CMS default configuration properties by applying all the 'CMS_'
prefixed enviroment variable values.
"""

from jsonpath_ng import jsonpath, parse
import argparse
import json
import logging
import os
import re
import sys

def cast_to(old, str_value):
    """Tranform string to the type of the given (first argument) value.
    """
    if old is None:
        return str_value
    if isinstance(old, (list, tuple)):
        return [cast_to(old[0], str_value)]
    if isinstance(old, dict):
        logging.error("Can not override dictionary value")
        return {}
    if isinstance(old, bool):
        return str_value in ["true", "True", "TRUE", "yes", "y"]

    old_type = type(old)
    return old_type(str_value)

def simple_map(storage, value, path):
    """Updates a storage property using the given JSON path
    """
    jsonpath_obj = parse(path)
    match = jsonpath_obj.find(storage)

    if any(match):
        if isinstance(value, str):
            jsonpath_obj.update(storage, cast_to(match[0].value, value))
        else:
            jsonpath_obj.update(storage, value)

def address_list_map(storage, value, path):
    """Updates a storage address mapping using the given JSON path
    """
    new_value = [val.split(':') for val in value.split(',')]
    simple_map(storage, new_value, path)

def list_map(storage, value, path):
    """Updates a storage property list using the given JSON path  with the given
    comma separated value
    """
    new_value = [val for val in value.split(',')]
    simple_map(storage, new_value, path)

def database_map (storage, value, path):
    """Database specific function, Updates a storage database property using the
    special "database.*" JSON path, replacing the given value from the database
    connection string.

    The database connection without any change should look like this:
    postgresql+psycopg2://cmsuser:your_password_here@localhost/cmsdb
    """
    basepath, override_key = path.split('.')
    jsonpath_obj = parse(basepath)

    old_value = jsonpath_obj.find(storage)[0].value
    m = re.search(r'postgresql\+psycopg2://(?P<user>\w+):(?P<pswd>[^\@]+)@(?P<host>[^:/]+)(:(?P<port>\d+))?/(?P<name>.+)', old_value)

    coordinates = {
        "name": m.group('name'),
        "user": m.group('user'),
        "pswd": m.group('pswd'),
        "host": m.group('host'),
        "port": m.group('port') if m.group('port') else 5432
    }
    coordinates[override_key] = value

    new_value = "postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{name}".format(**coordinates)
    jsonpath_obj.update(storage, new_value)

def set_configurations(config, overrides):
    """Iterates thought overrides map and update the configurations related to
    them.
    """
    for name, value in overrides.iteritems():
        if name not in override_mappings:
            continue
        path, map_func = override_mappings[name]
        map_func(config, value, path)

# Auto-generated value
override_mappings = {"GLOBAL_TMP_DIR":("temp_dir",simple_map),"GLOBAL_BACKDOOR":("backdoor",simple_map),"GLOBAL_COOKIE_SCRT":("secret_key",simple_map),"GLOBAL_DEBUG":("tornado_debug",simple_map),"ADDR_LOG_SRV":("core_services.LogService",address_list_map),"ADDR_RSCR_SRV":("core_services.ResourceService",address_list_map),"ADDR_SCOR_SRV":("core_services.ScoringService",address_list_map),"ADDR_CHCK_SRV":("core_services.Checker",address_list_map),"ADDR_EVAL_SRV":("core_services.EvaluationService",address_list_map),"ADDR_CWS":("core_services.ContestWebServer",address_list_map),"ADDR_ADMIN_WS":("core_services.AdminWebServer",address_list_map),"ADDR_PROXY_SRV":("core_services.ProxyService",address_list_map),"ADDR_PRINT_SRV":("core_services.PrintingService",address_list_map),"ADDR_WORKERS":("core_services.Worker",address_list_map),"ADDR_TFILE_CACHER":("other_services.TestFileCacher",address_list_map),"DB_USER":("database.user",database_map),"DB_PSWD":("database.pswd",database_map),"DB_NAME":("database.name",database_map),"DB_HOST":("database.host",database_map),"DB_PORT":("database.port",database_map),"DB_DEBUG":("database_debug",simple_map),"DB_2PHASE_COMMIT":("twophase_commit",simple_map),"WRK_KEEP_SANDBOX":("keep_sandbox",simple_map),"WRK_MAX_FILE_SIZE":("max_file_size",simple_map),"CWS_LISTEN_ADDR":("contest_listen_address",list_map),"CWS_LISTEN_PORT":("contest_listen_port",list_map),"CWS_COOKIE_TTL":("cookie_duration",simple_map),"CWS_PROXY_COUNT":("num_proxies_used",simple_map),"CWS_KEEP_FILE_UPLOAD":("submit_local_copy",simple_map),"CWS_FILE_UPLOAD_PATH":("submit_local_copy_path",simple_map),"CWS_ENTRY_UPLOAD_LIMIT":("max_submission_length",simple_map),"CWS_INPUT_UPLOAD_LIMIT":("max_input_length",simple_map),"WS_ADMIN_LISTEN_ADDR":("admin_listen_address",list_map),"WS_ADMIN_LISTEN_PORT":("admin_listen_port",list_map),"WS_ADMIN_COOKIE_TTL":("admin_cookie_duration",simple_map),"RANK_URL":("rankings",simple_map),"RANK_CERT":("https_certfile",simple_map)}

def main():
    """Parse arguments and print CMS configuration to STDOUT.
    """
    parser = argparse.ArgumentParser(description=__doc__[:__doc__.find("."):])
    parser.add_argument("baseconf", help="Initial configuration filepath")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.DEBUG if args.verbose else logging.ERROR)

    logging.info("Base configuraiton filepath: %s", args.baseconf)
    with open(args.baseconf) as config_file:
        config = json.load(config_file)

    prop_names = filter(lambda k: k.startswith('CMS_'), os.environ)
    overrides = {key[4:]: os.environ[key] for key in prop_names}
    logging.info("Overrides to map: %s", str(overrides))

    set_configurations(config, overrides)

    print json.dumps(config, indent=2)

if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(-1)
