#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from setuptools import setup
from setuptools.command import install, test
from pip.req import parse_requirements


__version__ = '0.1.0'


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

class Install(install.install):
    def run(self):
        install.install.run(self)
        virtual_env = os.environ.get('VIRTUAL_ENV', sys.prefix)
        path = os.path.join(virtual_env, 'etc', 'wowhua_admin.d')
        if not os.path.isdir(path):
            os.makedirs(path)
            print "Created Ticket Center app conf directory: " + path


class PyTest(test.test):
    def finalize_options(self):
        test.test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

install_reqs = parse_requirements('requirements.txt')
install_requires = [str(ir.req) for ir in install_reqs]
install_requires.extend(
    ['sallyconf==1.1.0',
     'wowhuaDB>=0.1.3',
     'zchLogger>=0.1.2',
     ]
)

tests_require = ['pytest==2.5.1', 'pytest-cov==1.6']
develop_require = tests_require + [
    'Sphinx>=1.2.1', 'pylint==1.1.0', 'mock==1.0.1',
    'fig>=1.0.1'
]

setup(
    name='wowhuaAdmin',
    version=__version__,
    description='',
    long_description=readme + '\n\n' + history,
    author='Skyrim',
    author_email='skyrim@zch168.net',
    url='http://code.zch168.net/hg/wowhua_admin',
    packages=[
        'wowhua_admin',
    ],
    package_dir={'wowhua_admin': 'wowhua_admin'},
    include_package_data=True,
    data_files=[('etc', ['wowhua_admin/conf/wowhua_admin.ini',
                         'wowhua_admin/conf/wowhua_admin_spec.ini'])],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'develop': develop_require,
        'test': tests_require
    },
    scripts=[
        'scripts/run_wowhua_admin.py',
    ],
    zip_safe=False,
    keywords='wowhua_admin',
    cmdclass={'install': Install},
)
