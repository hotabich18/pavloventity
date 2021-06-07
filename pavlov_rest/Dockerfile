ARG PYTHON_BASE_IMAGE=python:3.7.9-buster
FROM $PYTHON_BASE_IMAGE

ARG COMMIT=master

EXPOSE 5000

WORKDIR /base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        locales && \
    printf '%s\n%s\n' 'en_US.UTF-8 UTF-8' 'ru_RU.UTF-8 UTF-8' >> /etc/locale.gen && \
    locale-gen && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
        rm -rf /var/lib/apt/lists/* && \
        pip install virtualenv==16.7.5 && \
        virtualenv venv && \
        mkdir -p /venv/dp_internal_token_dir && \
    rm -rf /root/.cache

ENV PATH=/base/venv/bin:$PATH
ENV LANG='en_US.UTF-8' LANGUAGE='en_US.UTF-8' LC_ALL='en_US.UTF-8'

RUN git clone https://github.com/deepmipt/DeepPavlov.git && \
    cd DeepPavlov && \
    git checkout $COMMIT && \
    python setup.py develop && \
    python -c 'import deeppavlov.models' && \
    rm -rf /root/.cache

CMD if [ ! -z $COMMIT ]; then \
        cd /base/DeepPavlov && \
        git fetch --all --tags --prune && \
        git checkout $COMMIT && \
        python setup.py develop && \
        python -c 'import deeppavlov.models'; \

    fi && \
    if [ -d /venv/$CONFIG ]; then \
        PATH=/venv/$CONFIG/bin:$PATH; \
    else \
        python -m deeppavlov install $CONFIG && \
        if [ ! -d /venv/dp_internal_token_dir ]; then \
            mkdir /venv/$CONFIG && \
            cp -R /base/venv/* /venv/$CONFIG && \
            sed -i "\|VIRTUAL_ENV=|s|/base||g" "/venv/"$CONFIG"/bin/activate"; \
        fi; \
    fi && \
    python -m deeppavlov riseapi $CONFIG -p $PORT $PARAMS