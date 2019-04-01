from setuptools import setup, find_packages

setup(name='flow_codegen',
      packages=find_packages(),
      package_data={'': ['*.tx']},
      install_requires=["textx", "click"],
      entry_points={
          'textx_generators': [
              'flow_dsl_plantuml=flow_codegen.generators:flow_pu',
          ]
      },
      )
