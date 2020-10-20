#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

# !/bin/python


import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="pymasternode",
    version="1.0.0",
    description="Large-scale automated masternode setup",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/JonasMuehlmann/pymasternode",
    author="Jonas Muehlmann",
    author_email="jonasmuehlmann@protonmail.com",
    license="GPL-3",
    packages=["pymasternode"],
    install_requires=[
        "html2text",
        "attrs",
        "bcrypt",
        "certifi",
        "cffi",
        "chardet",
        "cryptography",
        "gevent",
        "greenlet",
        "idna",
        "more-itertools",
        "packaging",
        "parallel-ssh",
        "paramiko",
        "pluggy",
        "py",
        "pycparser",
        "PyNaCl",
        "pyparsing",
        "requests",
        "six",
        "ssh2-python",
        "urllib3",
        "vultr",
        "wcwidth"
    ]
)
