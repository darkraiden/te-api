#!/bin/bash

pip install flask \
            flask-restful \
            pycurl \
            MySQL-python \
            pymysql
python /srv/api/api.py
