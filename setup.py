from setuptools import find_packages, setup


f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='tastytrade',
    version='8.2',
    description='An unofficial SDK for Tastytrade!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Graeme Holliday',
    author_email='graeme.holliday@pm.me',
    url='https://github.com/tastyware/tastytrade',
    license='MIT',
    install_requires=[
        'requests<3',
        'websockets>=11.0.3',
        'pydantic>=2.6.3',
        'pandas_market_calendars>=4.3.3',
        'fake_useragent>=1.5.1'
    ],
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'tastytrade': ['py.typed']},
    include_package_data=True
)
