# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("address_gen.pyx"),
    zip_safe=False,
)