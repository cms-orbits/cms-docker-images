FROM python:2.7-slim

ARG CMS_UID=1000
ARG CMS_GID=1000
ARG CMS_VERSION=v1.3.2

#
# Create 'cmsuser' user and group
#
RUN addgroup --gid ${CMS_GID} cmsuser \
    && adduser --disabled-login --uid ${CMS_UID} --gid ${CMS_GID} --gecos '' \
               --no-create-home --shell /bin/false cmsuser

#
# Install CMS with alongside its dependencies.
#
# The CMS 1.3.x releases require some extra steps due the dated 'bcrypt==2.0.0' 
# dependency, since it relies on 'gnu-crypt.h' glibc ~2.4 header which has 
# been replaced by crypt.h in glibc 2.24. The generated image layer will *only*  
# contain CMS binaries alongside the python modules and required shared objects.
RUN set -ex \
    && SAVED_PKGS="$(apt-mark showmanual)" \
    && apt-get update \ 
    && apt-get install -y --no-install-recommends \
        build-essential \
        gettext \
        iso-codes \
        shared-mime-info \
        stl-manual \
        libpq-dev \
        libyaml-dev \
        libffi-dev \
        libcups2-dev \
        libcap-dev \
        cgroupfs-mount \
        gcc \
        libc6 \
        bcrypt \
        linux-headers-amd64 \
        libpython-dev \
        linux-libc-dev \
        wget \
    \
    && BCRYPT_DIR=$(mktemp -d '/tmp/XXXXXX') \
    && pip download --no-cache-dir -d $BCRYPT_DIR bcrypt==2.0.0 \
    && tar -xvzC $BCRYPT_DIR -f $BCRYPT_DIR/bcrypt-2.0.0.tar.gz \
    && cd $BCRYPT_DIR \
    && sed -i '/gnu-crypt/d' bcrypt-2.0.0/src/crypt_blowfish-1.3/crypt.h \
    && pip install ./bcrypt-2.0.0 \
    \
    && wget -O cms.tar.gz https://github.com/cms-dev/cms/releases/download/${CMS_VERSION}/${CMS_VERSION}.tar.gz \
    && mkdir -p /usr/local/src/cms \
    && tar -xvzC /usr/local/src/cms --strip-components=1 -f cms.tar.gz \
    && rm cms.tar.gz \
    && cd /usr/local/src/cms \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir psycopg2-binary \
    && python ./prerequisites.py install_conf \
    && awk '!/assert_not_root/ || !f++' prerequisites.py > prerequisites-tweaked.py \
    && python ./prerequisites-tweaked.py build_l10n \
    && python ./prerequisites-tweaked.py build_isolate \
    && python ./prerequisites-tweaked.py install_isolate \
    && rm ./prerequisites-tweaked.py \
    && python ./setup.py install \
    && ldconfig \
    \
    && apt-mark auto '.*' > /dev/null \
    && apt-mark manual \
        iso-codes \
        shared-mime-info \
        libcap2 \
        $SAVED_PKGS \
    && find /usr/local -type f -executable -not \( -name '*tkinter*' \) -exec ldd '{}' ';' \
        | awk '/=>/ { print $(NF-1) }' \
        | sort -u \
        | xargs -r dpkg-query --search \
        | cut -d: -f1 \
        | sort -u \
        | xargs -r apt-mark manual \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

#
# Add entrypoint and config. generator scripts
#
COPY files/genconfig.py /usr/local/bin/genconfig.py
COPY 1.3/entrypoint.sh /entrypoint.sh

RUN chmod ugo+x /entrypoint.sh /usr/local/bin/genconfig.py

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["help"]
