from setuptools import setup
setup(
    name='resumos-anpuh-cli',
    version='0.1.1',
    packages=['resumosanpuh'],
    install_requires=['beautifulsoup4', 'requests', 'lxml', 'pandas'],
    entry_points={
        'console_scripts': [
            'resumosanpuh = resumosanpuh.__main__:main'
        ]
    })

