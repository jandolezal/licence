from setuptools import setup

setup(
    name='holders',
    version='0.0.1',
    packages=['holders', 'licenses'],
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'holders = holders.main:main',
            'licenses = licenses.main:main',
        ]
    }
)
