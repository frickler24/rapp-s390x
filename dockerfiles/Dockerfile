FROM python:3.9.10-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mariadb-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip \
    && pip install --upgrade pip

RUN mkdir -p /RApp
WORKDIR /RApp

COPY requirements/* ./
RUN pip install -r prod.txt

RUN useradd -ms /bin/bash rapp
USER rapp

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

