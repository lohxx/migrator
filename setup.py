from setuptools import setup, find_packages

setup(
    name='migrator',
    packages=['migrator'],
    version='0.1',
    install_requires=['Click', 'Flask', 'rauth', 'sqlalchemy', 'requests'],
    entry_points={
        'console_scripts': [
            'copy-playlist=migrator.cli:copy'    
        ]    
    }
)
