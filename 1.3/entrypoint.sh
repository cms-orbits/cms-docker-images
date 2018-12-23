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
        genconfig.py /usr/local/etc/cms.ranking.conf
        exec "$@"
    ;;
    "cmsWorker")
        echo "WARNING: THE CMS WORKER CONTAINER SHOULD ONLY RUN AS PRIVILEGED"
    ;&
    "cms"*)
        genconfig.py /usr/local/etc/cms.conf
        exec "$@"
    ;;
    *)
        exec "$@"
    ;;
esac
