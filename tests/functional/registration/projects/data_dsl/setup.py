from setuptools import setup, find_packages

setup(name='data_dsl',
      version='1.0.0',
      packages=find_packages(),
      package_data={'': ['*.tx']},
      install_requires=["textx", "types_dsl"],
      entry_points={
        'textx_languages': [
            'data_dsl = data_dsl:data_dsl',
          ]
      },
      )
