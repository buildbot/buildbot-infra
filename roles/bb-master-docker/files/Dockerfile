FROM nopush/buildbot-master-deps

RUN useradd --uid 1000 --create-home --shell /bin/bash bbuser

USER bbuser
RUN mkdir /home/bbuser/workdir
WORKDIR /home/bbuser/workdir

ARG BUILDBOT_REVISION=unknown
RUN git clone https://github.com/buildbot/buildbot.git /home/bbuser/workdir/buildbot
RUN cd /home/bbuser/workdir/buildbot && git checkout metabuildbot || git checkout master

RUN virtualenv --python=python3 /home/bbuser/buildbot_venv \
    && /home/bbuser/buildbot_venv/bin/pip install -U pip setuptools \
    && make -C /home/bbuser/workdir/buildbot frontend_deps \
    && cd /home/bbuser/workdir/buildbot \
    && /home/bbuser/buildbot_venv/bin/pip install \
        -r /home/bbuser/workdir/buildbot/requirements-ci.txt \
        psycopg2-binary==2.9.7 \
    && /home/bbuser/buildbot_venv/bin/pip install -e pkg \
    && for name in \
        master \
        www/base \
        www/grid_view \
        www/console_view \
        www/waterfall_view \
        ; \
        do \
            /home/bbuser/buildbot_venv/bin/pip install -e $name ; \
        done

RUN /home/bbuser/buildbot_venv/bin/buildbot create-master /home/bbuser/workdir

ARG METABBOTCFG_REVISION=unknown
RUN git clone https://github.com/buildbot/metabbotcfg.git /home/bbuser/workdir/metabbotcfg

RUN ln -s /home/bbuser/workdir/metabbotcfg/master.cfg /home/bbuser/workdir/master.cfg

ADD run_buildbot.sh /run_buildbot.sh

CMD ["/run_buildbot.sh"]
