from setuptools import setup

setup(name='music-overlay',
      version='1.0',
      author='Ilya Kurin',
      author_email='4uf04eg@gmail.com',
      description="Small overlay for managing music players",
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      packages=['Code'],
      install_requires=['PySide2', 'pynput', 'toml'],
      license='LICENCE',
      entry_points={
            'gui_scripts': ["music-overlay = Code.__main__:main"]
      }
)
