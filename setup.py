from setuptools import setup, find_packages


setup(
    name="ARION",
    version="0.4.0",
    license="MIT",
    author="Isaac Baek",
    author_email="isaac.baek@samsung.com",
    description="POS benchmark test framework",
    long_description=open("README.md").read(),
    packages=find_packages(exclude=["test"]),
    install_requires=[
        "matplotlib>=3.3.4",
        "numpy>=1.19.5",
        "packaging>=21.0"
    ]
)
