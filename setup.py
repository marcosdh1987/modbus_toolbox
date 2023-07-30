import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="modbus_toolbox",
    version="0.1.8",
    author="Marcos E Soto",
    author_email="marcos.esteban.soto@gmail.com",
    description="Modbus Toolbox",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcosdh1987/modbus_toolbox",
    packages=setuptools.find_packages(),
    # install req from requirements.txt
    install_requires=[
        req for req in open("requirements.txt").read().split("\n") if req
    ],
)
