import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="paladins_wrapper",
    version="0.0.1",
    author="Ernesto Alvarado",
    description="async wrapper for Paladins API",
    licence="GPLv3",
    long_description=long_description,
    long_description_content="text/markdown",
    url="https://github.com/ErnestoAlvarado/Paladins_API",
    packages=setuptools.find_packages(include=['paladins_api']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "Programming Language :: Python :: 3.7",
        "Natural Language :: English",

    ],
    python_requires='>=3.7',

)