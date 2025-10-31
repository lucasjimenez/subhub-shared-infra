from setuptools import setup, find_packages

setup(
    name="subhub-infra-shared",
    version="0.1.0",
    description="Shared infrastructure components for SubHub AI projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "azure-keyvault-secrets>=4.7.0",
        "azure-identity>=1.14.0",
        "snowflake-connector-python>=3.0.0",
        "httpx>=0.24.0",
        "pydantic>=2.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)