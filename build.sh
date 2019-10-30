#!/bin/bash
set -euo pipefail

GOAL=${1-default}

##
# Updates 'override_mappings' variable value within 'files/genconfig.py' script
# based on table for configuration name mapping in 'files/configuration_map.tsv'
# file
update_genconfig_map() {
    local map
    map=$(tail -n+2 files/configuration_map.tsv | awk '{print "\""$1"\""":" "(""\""$2"\""","$3")"}' | paste -sd,)
    sed -i "/# Auto-generated value/{n;s/override_mappings =.*/override_mappings = \{$map\}/}" files/genconfig.py
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
