import os

from setuptools import setup, find_packages


# include the non python files
def package_files(directory, strip_leading):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            package_file = os.path.join(path, filename)
            paths.append(package_file[len(strip_leading):])
    return paths


tests_require = ['pytest',
                 ]

setup(name='robocar-tflite-steering',
      version='0.1',
      description='Compute steering value with tensorflow lite.',
      url='https://github.com/cyrilix/robocar-tflite-steering',
      license='Apache2',
      entry_points={
          'console_scripts': [
              'rc-tflite-steering=steering.cli:execute_from_command_line',
          ],
      },
      setup_requires=['pytest-runner'],
      install_requires=['importlib',
                        'docopt',
                        'paho-mqtt'
                        ],
      tests_require=tests_require,
      extras_require={
          'tests': tests_require
      },

      include_package_data=True,

      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Artificial Intelligence',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: Apache 2 License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.

          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='selfdriving cars drive',

      packages=find_packages(exclude=(['tests', 'env'])),
      )
