import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='bookstore',
    version='1.0.0',
    url='https://github.com/karthikramasamy/cmpe-272/',
    license='BSD',
    maintainer='Karthik Ramasamy',
    description='The basic bookstore app built for the SJSU CMPE-272 Spring 2019 course.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'pymongo',
        'pyjwt',
        'authlib',  
        'six',
    ],
    extras_require={
        'test': [
            'mongomock',
            'pytest',
            'pytest-cov',
            'coverage',
        ],
    },
)
