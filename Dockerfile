FROM python:3.9.10-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       mariadb-client \
       vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

COPY requirements/* ./
RUN pip3 install -r prod.txt

# RUN mkdir -p /RApp/code
# WORKDIR /RApp/code
WORKDIR /RApp

# User nobody

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

