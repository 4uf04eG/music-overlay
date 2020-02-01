from setuptools import find_packages, setup
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='media-player-controller',
      version='1.0',
      author='Ilya Kurin',
      author_email='4uf04eg@gmail.com',
      description="Small player for managing other music players",
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      install_requires=['PySide2', 'pynput', 'toml'],
      keywords='player music media'
      )
