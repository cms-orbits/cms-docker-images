#!/bin/bash
set -euo pipefail

GOAL=${1-default}

##
# Updates 'OVERRIDE_MAPPINGS' constant value in 'files/genconfig.py' script
# based on the configuration name mapping table in 'files/configuration_map.tsv'
# file
update_genconfig_map() {
    local map
    map=$(tail -n+2 files/configuration_map.tsv | awk '{print "\""$1"\""":" "(""\""$2"\""","$3")"}' | paste -sd,)
    sed -i "/# Auto-generated value/{n;s/OVERRIDE_MAPPINGS =.*/OVERRIDE_MAPPINGS = \{$map\}/}" files/genconfig.py
}

##
# Mimicks goal based behavior of 'make' command, using the functions defined
# above
shift
case "$GOAL" in
  update-genconfig-envs)
    update_genconfig_map
    ;;
  *)
    echo ":: Unrecognized goal '${GOAL}'. Nothing to do."
    ;;
esac
