import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Auto Test",
    version = "0.1",
    author = "Chetan Sharma",
    author_email = "chetan.sharma@timesys.com",
    description = ("An automation tool execute driver tests on Remote Board using timesys Test tool. "),
    packages = ['src'],
    install_requires=['ConfigParser', 'paramiko', 'scp'],
    license  = "Timesys ",
)
