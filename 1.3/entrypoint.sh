#!/bin/bash -e
# shellcheck disable=SC2011

case "${1}" in
    "help")
        echo -n 'Run any CMS service, server or utility script as container. ' 
        echo 'The following are the main CMS starting scripts:'
        ls /usr/local/bin/cms{*Service,*Server,*Worker} | xargs -n1 basename | sed -e 's/^/- /'
        echo 'Please refer to the CMS manual for more information about their arguments or the available utility ones.'
    ;;
    "cmsRankingWebServer")
        genconfig.py --dry-run /usr/local/etc/cms.ranking.conf
        exec "$@"
    ;;
    "cmsWorker")
        echo "WARNING: THE CMS WORKER CONTAINER SHOULD ONLY RUN AS PRIVILEGED"
        genconfig.py --dry-run /usr/local/etc/cms.conf
        exec "$@"
    ;;
    "cms"*)
        genconfig.py --dry-run /usr/local/etc/cms.conf
        exec "$@"
    ;;
    *)
        exec "$@"
    ;;
esac
