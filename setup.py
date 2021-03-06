#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
avamar RESTful API
"""
from setuptools import setup, find_packages


setup(name="vlab-avamar-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2021.01.21',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_avamar_api' : ['app.ini']},
      description="avamar",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery']
      )
