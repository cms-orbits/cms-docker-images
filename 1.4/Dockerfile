FROM python:3.6-slim

ARG CMS_UID=1000
ARG CMS_GID=1000
ARG CMS_VERSION=v1.4.rc1

#
# Create 'cmsuser' user and group
#
RUN addgroup --gid ${CMS_GID} cmsuser \
    && adduser --disabled-login --uid ${CMS_UID} --gid ${CMS_GID} --gecos '' \
               --no-create-home --shell /bin/false cmsuser

#
# Install CMS with alongside its dependencies.
#
# The generated image layer will *only* contain CMS binaries alongside the
# python modules and required shared objects.
RUN set -ex \
    && SAVED_PKGS="$(apt-mark showmanual)" \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gettext \
        iso-codes \
        shared-mime-info \
        stl-manual \
        cppreference-doc-en-html \
        gcc \
        libc6 \
        libpq-dev \
        libcap-dev \
        libffi-dev \
        libyaml-dev \
        libcups2-dev \
        cgroupfs-mount \
        libpython3-dev \
        linux-libc-dev \
        linux-headers-amd64 \
        wget \
        zip \
    \
    && wget -O cms.tar.gz https://github.com/cms-dev/cms/releases/download/${CMS_VERSION}/${CMS_VERSION}.tar.gz \
    && mkdir -p /usr/local/src/cms \
    && tar -xvzC /usr/local/src/cms --strip-components=1 -f cms.tar.gz \
    && rm cms.tar.gz \
    && cd /usr/local/src/cms \
    && pip install --no-cache-dir -r requirements.txt \
    && python ./prerequisites.py --as-root build \
    && python ./prerequisites.py --yes --as-root install \
    && python ./setup.py install \
    \
    && pip install --no-cache-dir jsonpath-ng \
    \
    && ldconfig \
    \
    && apt-mark auto '.*' > /dev/null \
    && apt-mark manual \
        iso-codes \
        shared-mime-info \
        libcap2 \
        zip \
        stl-manual \
        cppreference-doc-en-html \
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
# Add entrypoint, config. generation scripts and required CMS directories
#
COPY files/genconfig.py /usr/local/bin/genconfig.py
COPY 1.4/entrypoint.sh /entrypoint.sh

RUN chmod ugo+x /entrypoint.sh /usr/local/bin/genconfig.py \
    && for n in log cache lib run; do mkdir -p /var/local/${n}/cms; \
      chown ${CMS_UID}:${CMS_GID} /var/local/${n}/cms; \
    done

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["help"]
