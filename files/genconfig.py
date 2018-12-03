#!/usr/bin/env python

"""Overrides CMS configuration properties with the existing 'CMS_' prefixed
enviroment variable values.

Each CMS configuration property is mapped as an enviroment variable in a similar
fashion as spring relaxed binding[0] does, where each property name is
transformed to upper case format using double underscore "__" as subschema
delimiter.

For example the "core_services.ResourceService" property can be overriden as
"CMS_CORE_SERVICES__RESOURCESERVICE"

[0] https://docs.spring.io/spring-boot/docs/current/reference/html/boot-features-external-config.html#boot-features-external-config-relaxed-binding
"""

import argparse
import json
import logging
import os
import sys

SPECIAL_PROPERTIES = ["core_services", "database"]

def prepare_core_services(config):
    """Replace any 'localhost' reference from 'config' map.
    """
    if "core_services" in config:
        services = config["core_services"]
        for service_name, service_coords in services.iteritems():
            for service_tuple in service_coords:
                service_tuple[0] = service_name.lower()
        config["_core_services"] = services
    return config

def set_configurations(base, overrides):
    """Insert generic configurations from 'overrides' map into the 'base' one.
    """
    for prop_name in SPECIAL_PROPERTIES:
        base[prop_name] = {}

    for path_str, value in overrides.iteritems():
        path = path_str.lower().split('__')
        try:
            set_prop(base, path, value)
        except KeyError:
            logging.error("Invalid CMS property: %s", ".".join(path))

def bake_special_confiurations(config):
    """Transform and insert 'database' and 'core_services' sections into the
    CMS configuration map.
    """
    db_coordinates = config["database"]
    if isinstance(db_coordinates, dict):
        config["database"] = gen_database_string(db_coordinates)

    if "_core_services" in config:
        config["core_services"] = gen_coreservices_map(
            config["_core_services"],
            config["core_services"])

        del config["_core_services"]

def gen_coreservices_map(default, override):
    """Transform and apply 'override' map into the given 'default' one.
    """
    override = coresservice_map_camelcases(override)

    for name, value in override.iteritems():
        if name in default:
            default[name] = transform_coreservice_map_value(value)
        else:
            logging.error("Can not find '%s' service", name)

    return default

def coresservice_map_camelcases(services):
    """Transform 'services' map string keys into camelcases (for specific
    scenarios).

    >>> coresservice_map_camelcases({"worker": "worker:1234"})
    {"Worker": "worker:1234"}
    >>> coresservice_map_camelcases({"contestwebserver": "cms:1234"})
    {"ContestWeServer": "cms:1234"}
    """
    return {key.capitalize().replace("web", "Web").replace("serv", "Serv"): services[key] for key in services}

def transform_coreservice_map_value(str_value):
    """Transform a comma separated host port string into a list of lists,
    just as used by CMS configuration.

    >>> transform_coreservice_map_value("thehost:3506")
    [["thehost",3506]]
    >>> transform_coreservice_map_value("onehost:3606,other,foobar:2356")
    [["onehost",3606],["foobar",2356]]
    """
    if str_value is None:
        return [[]]

    host_list = []

    for token in str_value.split(","):
        host_port = token.split(":")
        if len(host_port) == 2:
            host_port[1] = int(host_port[1])
            host_list.append(host_port)

    return host_list

def gen_database_string(overrides):
    """Generates postgresql connection string with the given overrides map.

    >>> gen_database_string({})
    postgresql+psycopg2://cmsuser:notsecure@postgresql:5432/cmsdb
    >>> gen_database_string({"user": "foobar", "host": "localhost"})
    postgresql+psycopg2://foobar:notsecure@postgresql:5432/cmsdb
    """

    db_str = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    db_coordinates = {
        "name": "cmsdb",
        "user": "cmsuser",
        "password": "notsecure",
        "host": "postgresql",
        "port": "5432"
    }
    db_coordinates.update(overrides)
    return db_str.format(**db_coordinates)

def set_prop(obj, path, value):
    """Set property 'value' into 'obj' using the given 'path' list.
    """
    logging.debug("Set %s", ".".join(path) + " = " + value)
    if isinstance(obj, dict):
        if len(path) == 1:
            old = obj[path[0]] if path[0] in obj else None
            obj[path[0]] = cast_to(old, value)
        else:
            set_prop(obj[path[0]], path[1:], value)
    else:
        logging.error("Unable to set property: %s", str(path))

def cast_to(old, str_value):
    """Tranform string to the type of the given (first argument) value.
    """
    if old is None:
        return str_value
    if isinstance(old, (list, tuple)):
        return [cast_to(old[0], str_value)]
    if isinstance(old, dict):
        logging.error("Can not override dictionary value ")
        return {}
    if isinstance(old, bool):
        return str_value in ["true", "True", "TRUE"]

    old_type = type(old)
    return old_type(str_value)


def main():
    """Parse arguments and updates CMS configuration files.
    """
    parser = argparse.ArgumentParser(description=__doc__[:__doc__.find("."):])
    parser.add_argument("targetconf", help="Configuration file path")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print to STDOUT the result instead of ovewriting \
                        target configuration file")
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level=logging.DEBUG if args.verbose else logging.ERROR)

    logging.info("Target configuraiton file: %s", args.targetconf)
    with open(args.targetconf) as config_file:
        config = json.load(config_file)
    config = prepare_core_services(config)

    prop_names = filter(lambda k: k.startswith('CMS_'), os.environ)
    overrides = {key[4:]: os.environ[key] for key in prop_names}
    logging.debug("Override map: %s", str(overrides))

    set_configurations(config, overrides)
    bake_special_confiurations(config)

    if args.dry_run:
        print(json.dumps(config, indent=2))
    else:
        with open(args.targetconf, 'w') as config_file:
            config_file.write(json.dumps(config, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
