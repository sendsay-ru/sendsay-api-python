#!/usr/bin/env python
from setuptools import setup, find_packages

exec(open("sendsay/version.py").read())

setup(
    name='sendsay-api-python',
    version=__version__,
    description='The Sendsay API client library.',
    author='Vadim Khakulov',
    author_email='vadim.khakulov@gmail.com',
    maintainer='Vadim Khakulov',
    maintainer_email='vadim.khakulov@gmail.com',
    url='https://github.com/sendsay-ru/sendsay-api-python',
    license='Apache',
    test_suite='test.test_sendsay',
    packages=find_packages(),
    include_package_data=True,
    long_description=open("README.rst").read(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    install_requires=[
        'requests',
        'ndg-httpsclient'
    ],
)
