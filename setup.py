#!/usr/bin/env python
from setuptools import setup

exec(open("sendsay/version.py").read())

setup(
    name='sendsay',
    version=__version__,
    description='The Sendsay API client library.',
    author='Sendsay',
    maintainer='Vadim Khakulov',
    maintainer_email='vadim.khakulov@gmail.com',
    url='https://github.com/axens/sendsay',
    license='Apache',
    test_suite='test.test_sendsay',
    packages=["sendsay","test"],
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
    ],
)
