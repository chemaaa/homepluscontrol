import setuptools
from setuptools.command.test import test as TestCommand
import sys

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
    license="GPLv3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chemaaa/homepluscontrol",
    packages=setuptools.find_packages(exclude=["test", "test.*"]),
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
    python_requires=">=3.6",
    install_requires=[
        "aiohttp>=3.7.1",
        "PyJWT>=1.7.1",
        "yarl>=1.4.2",
    ],
)
