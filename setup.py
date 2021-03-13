import setuptools
from setuptools.command.test import test as TestCommand

import homepluscontrol

with open("README.md", "r") as fh:
    long_description = fh.read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setuptools.setup(
    name="homepluscontrol",
    version=homepluscontrol.version,
    author="chemaaa",
    author_email="chemaaar@gmail.com",
    description="Python-based API to interact with the Legrand Home + Control interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chemaaa/homepluscontrol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.6',
    install_requires=[
        'aiohttp==3.7.1',
        'aioresponses>=0.7.1',
        'alabaster>=0.7.12',
        'async-timeout>=3.0.1',
        'attrs==19.3.0',
        'Babel>=2.9.0',
        'certifi>=2020.11.8',
        'cffi>=1.14.3',
        'chardet>=3.0.4',
        'coverage>=5.3',
        'cryptography==3.2',
        'docutils>=0.16',
        'idna>=2.10',
        'imagesize>=1.2.0',
        'iniconfig>=1.1.1',
        'Jinja2>=2.11.2',
        'MarkupSafe>=1.1.1',
        'multidict>=5.0.2',
        'oauthlib>=3.1.0',
        'packaging>=20.4',
        'pip-autoremove>=0.9.1',
        'pluggy>=0.13.1',
        'py>=1.9.0',
        'pycparser>=2.20',
        'Pygments>=2.7.2',
        'PyJWT==1.7.1',
        'pyparsing>=2.4.7',
        'pytest>=6.1.2',
        'pytest-cov>=2.10.1',
        'pytz>=2020.4',
        'requests>=2.25.0',
        'requests-oauthlib>=1.3.0',
        'six>=1.15.0',
        'snowballstemmer>=2.0.0',
        'Sphinx>=3.3.1',
        'sphinxcontrib-applehelp>=1.0.2',
        'sphinxcontrib-devhelp>=1.0.2',
        'sphinxcontrib-htmlhelp>=1.0.3',
        'sphinxcontrib-jsmath>=1.0.1',
        'sphinxcontrib-qthelp>=1.0.3',
        'sphinxcontrib-serializinghtml>=1.1.4',
        'toml>=0.10.2',
        'typing-extensions>=3.7.4.3',
        'urllib3>=1.26.2',
        'yarl==1.4.2',
    ]
)
