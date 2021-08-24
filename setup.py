from setuptools import setup
setup(
    name = 'resumos-anpuh',
    version = '0.1.0',
    packages = ['resumos-anpuh'],
    entry_points = {
        'console_scripts': [
            'resumos-anpuh = resumos-anpuh.__main__:main'
        ]
    })
