import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloudssh-swbsf",
    version="0.0.1",
    author="Steven Wallimann",
    author_email="steven.wallimann@gmail.com",
    description="CloudSSH allow to dynamically find a SSH connection path, whether you have a bastion host or not",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/swbsf/cloudssh",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
