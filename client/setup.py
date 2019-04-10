from setuptools import setup

from rq_client import __version__

setup(
    name='rq_client',
    version=__version__,
    packages=['rq_client'],
    install_requires=[
       'requests',
    ]
)
