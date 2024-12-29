from setuptools import setup, find_packages

setup(
    name="Ecommercebot",
    version="0.0.1",
    author="aditya",
    author_email="adityacool2134@gmail.com",
    packages=find_packages(),
    install_requires=['langchain-astradb','langchain ','langchain-openai','datasets','pypdf','python-dotenv','flask']
)