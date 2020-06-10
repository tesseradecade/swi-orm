import setuptools

setuptools.setup(
    name="prolog",
    version="0.1",
    author="timoniq",
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    url="https://github.com/tesseradecade/prolog",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=["pexpect", "swipy"],
)
