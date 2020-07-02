import setuptools
from binance import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crypto.com",
    version=__version__,
    author="Th0rgal",
    author_email="thomas.marchand@tuta.io",
    description="A python3 crypto.com API wrapper powered by modern technologies such as asyncio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.io/crypto.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
