from setuptools import setup

APP = ['src/client.py']
OPTIONS = {'argv_emulation': True, 'includes': ['EXTERNAL LIBRARY'], }

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
