from setuptools import find_packages, setup

from tastytrade import VERSION


f = open('README.rst', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='tastytrade',
    version=VERSION,
    description='An unofficial SDK for Tastytrade!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/x-rst',
    author='Graeme Holliday',
    author_email='graeme.holliday@pm.me',
    url='https://github.com/tastyware/tastytrade',
    license='MIT',
    install_requires=[
        'requests<3',
        'dataclasses',
        'websockets>=11.0.3',
        'pydantic>=1.10.7'
    ],
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    include_package_data=True
)
