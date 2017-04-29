from setuptools import setup, find_packages

setup(
    name='animism',
    version='0.1',
    packages=find_packages(),

    install_requires=['progressbar2>=3.18.0'],

    author='Joel Holdsworth',
    author_email='joel@airwebreathe.org.uk',
    description='A package for rendering animations programatically',
    license='GPLv2',
    url='http://github.com/jhol/animism'
)
