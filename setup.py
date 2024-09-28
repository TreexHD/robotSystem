from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'this is the robot System library'
LONG_DESCRIPTION = 'A package that allows easy access to all functions of the robot'

# Setting up
setup(
    name="robotsystem",
    version=VERSION,
    author="TreexHD",
    author_email="<no.mail>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ]
)