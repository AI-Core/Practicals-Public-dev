from setuptools import setup, find_packages

setup(name='content-projects',
      version='1.0',
      packages=find_packages(),
      install_requires=[
          'PyYaml',
          'boto3',
          'requests',
          'nbformat==5.7.1',
      ]
      )
