import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="homepluscontrol",
    version="0.0.1",
    author="chemaaa",
    author_email="chemaaar@gmail.com",
    description="Python-based API to interact with the Legrand Home + Control interface",
    long_description=long_description,
    long_description_ctontent_type="text/markdown",
    url="https://github.com/chemaaa/homepluscontrol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
)