from setuptools import setup, find_packages

setup(name='types_dsl',
      version='1.0.0',
      packages=find_packages(),
      package_data={'': ['*.tx']},
      install_requires=["textx"],
      entry_points={
        'textx_languages': [
            'types_dsl = types_dsl:types_dsl',
        ]
      },
      )
