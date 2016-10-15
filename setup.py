import os
import re
from setuptools import setup, find_packages


current_path = os.path.abspath(os.path.dirname(__file__))
tailsocket_path = os.path.join(current_path, 'tailsocket')


def read(filepath):
    with open(filepath, 'r') as fd:
        return fd.read()


def find_version():
    version_path = os.path.join(tailsocket_path, 'version.py')
    contents = read(version_path)

    version_match = re.match(r'^__version__ = [\'"]([\d\.]+)[\'"]', contents)
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


def get_readme():
    readme_path = os.path.join(current_path, 'README.rst')
    return read(readme_path)


setup(
    name='tailsocket',
    version=find_version(),
    packages=find_packages(),
    url='https://github.com/yeraydiazdiaz/tailsocket',
    license='MIT',
    author='Yeray Diaz Diaz',
    author_email='yeraydiazdiaz@gmail.com',
    description='A WebSocket application to tail files.',
    long_description=get_readme(),
    include_package_data=True,
    install_requires=['tornado==4.4.1'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Topic :: System :: Logging",
    ],
    entry_points={
        'console_scripts': [
            'tailsocket-server = tailsocket.application:main',
        ]
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        ":sys_platform=='linux'": [
            'pyinotify==0.9.6',
        ],
    }
)
