FROM rokubun/python:numpy-slim-buster as development

LABEL authors="Miquel Garcia"
LABEL email="info@rokubun.cat"

ENV JASON_API_KEY="ApiKey from Jason service"
ENV JASON_SECRET_TOKEN="Jason User secret token here"

WORKDIR /jason-gnss

COPY . .

RUN apt-get update \
 && apt-get install -y git \
 && pip install -e .

CMD sh

# ---------------- Stage -------------------------------------------------------

FROM development as production

WORKDIR /jason-gnss

ENV JASON_API_KEY="ApiKey from Jason service"
ENV JASON_SECRET_TOKEN="Jason User secret token here"

RUN apt-get update \
 && apt-get install -y git \
 && python setup.py install \
 && apt autoremove -y git

