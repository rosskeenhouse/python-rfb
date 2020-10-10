import re

from setuptools import setup

vers = re.compile(r'__version__\s*=\s*"(.*)"')
with open("src/rfb/__init__.py", "r") as f:
  version = vers.search(f.read(), re.M).group(1)

setup(
  name="rfb",
  version=version
)
