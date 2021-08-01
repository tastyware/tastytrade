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
    url='https://github.com/Graeme22/tastyworks-api',
    license='Apache',
    install_requires=[
        'aiohttp>=3.7.4',
        'requests>=2.26.0',
    ],
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    include_package_data=True,
)
