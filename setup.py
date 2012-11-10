from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = [
    'pyramid',
    'repoze.workflow',
    'venusian',
]

tests_require = [
    "nose",
    "webtest",
]

setup(name='pyramid_workflow',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
        "testing": tests_require,
      },
      test_suite="pyramid_workflow",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
