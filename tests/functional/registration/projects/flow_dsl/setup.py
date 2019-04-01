from setuptools import setup, find_packages

setup(name='flow_dsl',
      packages=find_packages(),
      package_data={'': ['*.tx']},
      install_requires=["textx"],
      entry_points={
        'textx_languages': [
            'flow_dsl = flow_dsl:flow_dsl',
          ]
      },
      )
