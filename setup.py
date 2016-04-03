#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='qingfanyi',
    version='1.2.0',
    packages=find_packages(),
    url='https://github.com/rohanpm/qingfanyi',
    license='GPL',
    author='Rohan McGovern',
    author_email='rohan@mcgovern.id.au',
    description='Chinese to English dictionary lookup tool',
    long_description=('Qingfanyi is a Chinese to English dictionary/translation tool. '
                      'It uses the AT-SPI accessibility APIs on Linux desktop systems '
                      'to capture Chinese text on the currently active window and '
                      'provide an interactive lookup on demand.'),
    install_requires=['ewmh==0.1.3',
                      #'pyatspi',
                      # 'gi',
                      'marisa_trie==0.7.2'],
    entry_points={
        'console_scripts': [
            'qfy=qingfanyi.process.main:run'
        ]
    },
    package_data = {
        'qingfanyi': ['data/*.txt'],
    }
)
