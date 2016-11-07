from setuptools import setup, find_packages
import os

version = '1.1ftw'

tests_require = [
    'plone.app.testing',
    ]

setup(name='cs.auth.googleplus',
      version=version,
      description="Plone package to provide Google+ authentication",
      long_description=open("README.md").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone pas login google googleplus',
      author='Mikel Larreategi',
      author_email='mlarreategi@codesyntax.com',
      url='https://github.com/codesyntax/cs.auth.googleplus',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', 'cs.auth'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'collective.beaker',
          'requests',
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
