from setuptools import find_packages, setup

from tastyworks.utils import VERSION


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='tastyworks-api',
    version=VERSION,
    description='An unofficial API for Tastyworks!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Graeme Holliday',
    author_email='graeme.holliday@pm.me',
    url='https://github.com/tastyware/tastyworks-api',
    license='Apache',
    install_requires=[
        'aiohttp<4',
        'requests<3',
        'aiocometd @ git+https://github.com/Graeme22/aiocometd@0.4.5.3#egg=aiocometd',
        'dataclasses'
    ],
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    include_package_data=True,
)
