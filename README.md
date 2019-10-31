# CMS (un-official) Docker images

**Warning**: This project packages the [CMS](https://github.com/cms-dev/cms)
platform core components as Docker images, but still this approach is not
recognized neither tested by the CMS core development team, so if you are
planning to host a local programming contest using the aforementioned software
is *highly recommended* to follow the installation steps described in the
[CMS manual](https://cms.readthedocs.io/en/latest/Installation.html) instead.

## Why?

**tl;dr** By packagign CMS platform components as Docker image the installation
and deployment process time and complexity *should* be reduced.

## Make it run

By desing [CMS](https://cms.readthedocs.io/en/latest/Introduction.html#services)

spins up about 10 separated process from the same code base. Because of this the
CMS Docker image takes a bit different approach, by allowing the user to spin a
single CMS process (Service, server, worker or utility) per container,
delegating the orchestration to a separated component like
[docker-compose](https://docs.docker.com/compose/), or
[Kubernetes](https://kubernetes.io/), moving away from `cmsResourceService`
usage as process supervisor.

In order to run a CMS process you only need to use the `docker container run`
command and pass the CMS process name and its arguments at the end of the
command line. By default when no argument is present the CMS Docker image will
display a help message.

```shell
$ docker container run --rm cmsorbits/cms
Run any CMS service, server or utility script as container. The following are the main CMS starting scripts:
- cmsAdminWebServer
- cmsContestWebServer
- cmsEvaluationService
- cmsLogService
- cmsPrintingService
- cmsProxyService
- cmsRankingWebServer
- cmsResourceService
- cmsScoringService
- cmsWorker
Please refer to the CMS manual further information about their arguments or the available utility ones.
```

For example if you need to spin up the CMS AdminWebServer, using its default
configuration and port arrangement you will need to prompt a command similar to
this one:

```shell
docker container run --rm -p 8089:8089 jossemargt/cms cmsAdminWebServer
```

### Configuration

All the intrinsic configurations can be overridden by exposing `CMS_` prefixed
environment variables with the desired value. For example in order to override
the `core_services.ContestWebServer` configuration in the `AdminWebServer`, you
could start the Docker container with the following command:

```shell
docker container run --rm -p 8089:8089 -e 'CMS_ADDR_CWS=10.10.37.10' jossemargt/cms cmsAdminWebServer
```

Bear in mind this process can be simplied using `docker-compose` which
allows you to provide those values directly in the `docker-compose.yml` or
`docker-compose.override.yml` files using the
[environment](https://docs.docker.com/compose/compose-file/#environment) block.

Since the JSON fields in the `cms.conf` and `cms.ranking.conf` files do not
follow any naming convention, each configuration had to be mapped into an
specific environment variable name. In other words, when you need to override a
configuration property you should check its environment variable name in the
following table:

Conf. JSON Path | Env. Variable name | Default value | Description
--- | --- | --- | ---
core_services.AdminWebServer | CMS_ADDR_ADMIN_WS | localhost:21100 | Network address to communicate with `AdminWebServer` through RPC protocol
core_services.Checker | CMS_ADDR_CHCK_SRV | localhost:22000 | Network address to communicate with `Checker` through RPC protocol
core_services.ContestWebServer | CMS_ADDR_CWS | localhost:21000 | Network address to communicate with `ContestWebServer` through RPC protocol
core_services.EvaluationService | CMS_ADDR_EVAL_SRV | localhost:25000 | Network address to communicate with `EvaluationService` through RPC protocol
core_services.LogService | CMS_ADDR_LOG_SRV | localhost:29000 | Network address to communicate with `LogService` through RPC protocol
core_services.PrintingService | CMS_ADDR_PRINT_SRV | localhost:25123 | Network address to communicate with `PrintingService` through RPC protocol
core_services.ProxyService | CMS_ADDR_PROXY_SRV | localhost:28600 | Network address to communicate with `ProxyService` through RPC protocol
core_services.ResourceService | CMS_ADDR_RSCR_SRV | localhost:28000 | Network address to communicate with `ResourceService` through RPC protocol
core_services.ScoringService | CMS_ADDR_SCOR_SRV | localhost:28500 | Network address to communicate with `ScoringService` through RPC protocol
core_services.Worker | CMS_ADDR_WORKERS | localhost:26000,localhost:26001 | Network address to communicate with `Worker`'s through RPC protocol
other_services.TestFileCacher | CMS_ADDR_TFILE_CACHER | localhost:27501 | Network address to communicate with `TestFileCacher` through RPC protocol
database.host | CMS_DB_HOST | localhost | PostgreSQL datasource host
database.port | CMS_DB_PORT | 5432 | PostgreSQL datasource port
database.name | CMS_DB_NAME | cmsdb | PostgreSQL datasource schema name
database.user | CMS_DB_USER | cmsuser | PostgreSQL datasource username
database.pswd | CMS_DB_PSWD | notsecure | PostgreSQL datasource password
database_debug | CMS_DB_DEBUG | false | Whether SQLAlchemy prints DB queries on stdout.
twophase_commit | CMS_DB_2PHASE_COMMIT | false | Whether to use two-phase commit.
cookie_duration | CMS_CWS_COOKIE_TTL | 10800 | Contest login cookie duration in seconds
max_submission_length | CMS_CWS_ENTRY_UPLOAD_LIMIT | 100000 | Maximum size of an Entry in bytes.
submit_local_copy | CMS_CWS_KEEP_FILE_UPLOAD | true | Wheter CWS should write Entry to disk before storing them in
submit_local_copy_path | CMS_CWS_FILE_UPLOAD_PATH | %s/submissions/ | Local path to store Entries on disk (if enabled)
max_input_length | CMS_CWS_INPUT_UPLOAD_LIMIT | 5000000 | Maximum size of a user_test input in bytes.
contest_listen_address | CMS_CWS_LISTEN_ADDR | "" | Network address that CWS should allow to server http content (`""` is the same as `"0.0.0.0"`)
contest_listen_port | CMS_CWS_LISTEN_PORT | 8888 | Port that CWS should use to server http content
num_proxies_used | CMS_CWS_PROXY_COUNT | 0 | Number of http proxies in front of CWS (xsrf security)
backdoor | CMS_GLOBAL_BACKDOOR | false | Whether to have **the** backdoor enabled
secret_key | CMS_GLOBAL_COOKIE_SCRT | 8e045a51e4b102ea803c06f92841a1fb | Secret text to hash all the http cookies
tornado_debug | CMS_GLOBAL_DEBUG | false | Whether to let Tornado to write debug message on STDOUT
temp_dir | CMS_GLOBAL_TMP_DIR | /tmp | Temporary file diretory path
https_certfile | CMS_RANK_CERT | None | Ranking web server TLS certificate filepath
rankings | CMS_RANK_URL | http://usern4me:passw0rd@localhost:8890/ | Ranking web server connection URL
keep_sandbox | CMS_WRK_KEEP_SANDBOX | false | Whether the Entry sandbox should be persisted in worker filesystem
max_file_size | CMS_WRK_MAX_FILE_SIZE | 1048576 | Maximum file size allowed by the worker
admin_cookie_duration | CMS_WS_ADMIN_COOKIE_TTL | 36000 | AdminServer login cookie duration in seconds
admin_listen_address | CMS_WS_ADMIN_LISTEN_ADDR | "" | Network address that the AdminServer should allow to server http content (`"" =="0.0.0.0"`)
admin_listen_port | CMS_WS_ADMIN_LISTEN_PORT | 8889 | Port that the AdminServer should use to server http content
bind_address (ranking.conf) | RANK_LISTEN_ADDR | "" | Network address that the RankingServer should allow to server http content (`"" =="0.0.0.0"`)
http_port (ranking.conf) | RANK_LISTEN_PORT | 8890 | Port that the RankingServer should use to server http content
username (ranking.conf) | RANK_USER | usern4me | RankingServer allowed username (must match with the one in `CMS_RANK_URL`)
password (ranking.conf) | RANK_PSWD | passw0rd | RankingServer password (must match with the one in `CMS_RANK_URL`)

## Build it locally

If you are looking to extend or debug the CMS Docker image, you will need to build
it in your local environment. For this you will need:

1. Docker engine 17.x or greater
2. POSIX complaint shell
3. Python virtual environment with Python 2.7.x + `jsonpath-ng` (only if you need to modify `files/genconfig.py`)

### Change a configuration mapping (JSON Path to ENV)

Each CMS and CMS Ranking configuration property had been mapped inside the
`files/configuration_map.tsv` file, where each line contains the following:

1. Environment variable name `env_name`. Defines the Env. variable name that will containe the conf. override.
2. Conf. property JSON path `JSON_path`. Defines the configuration property to be overriden.
3. Mapping function `map_func`. Sets the function inside of `genconfig.py` script that interprets the property.
4. Sample  value `sample_file_value`. For internal documentation only, it has the value that comes from the CMS sample configurations.

If you want to rename or add a new configuration override, you must comply with
the aforementioned values and then run the `./build.sh update-genconfig-envs`
command in order to update the `genconfig.py` internal mapping.

## License

The source code within this respoitory is licensed under the **MIT License** -
see the [LICENSE](LICENSE) file for details.

The software called [CMS](https://github.com/cms-dev/cms) packaged as Docker
images by this repository is licensed under **GNU Affero General Public License v3.0** -
see its [LICENSE](https://github.com/cms-dev/cms/blob/master/LICENSE.txt) file
for details.

## Credits

- [CMS](https://github.com/cms-dev/cms) platform and [CMS community](https://github.com/cms-dev/cms/blob/master/AUTHORS.txt)
