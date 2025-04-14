from setuptools import setup, find_packages

setup(
    name="sensor_visualization",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5.0",
        "numpy>=1.20.0",
    ],
    python_requires=">=3.6",
)