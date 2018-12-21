import os

from setuptools import setup
from halo.settings import DEBUG, VERSION

if DEBUG:
    print("You cannot build or install in debug mode.")
    exit(1)


def get_long_description():
    description = []
    with open('README.md') as f:
        description.append(f.read())


setup(name='Halo',
      version=VERSION,
      description='The weather app.',
      long_description=get_long_description(),
      author='Cijo Saju',
      author_email='hello@cijo.me',
      license='MIT',
      packages=['halo'],
      url='https://github.com/cijo7/Halo',
      entry_points={
          "gui_scripts": [
              "halo = halo.__main__:main",
          ]
      },
      setup_requires=["pycairo==1.18.0"],
      install_requires=[
          "requests",
          "pytz",
          "numpy",
          "pyparsing",
          "cycler",
          "six",
          "chardet",
          "idna==2.7",
          "kiwisolver",
          "python-dateutil",
          "urllib3",
          "certifi",
          "pygobject==3.30.4",
          "matplotlib",
          "typing"
      ],
      data_files=[
          (os.getenv('HOME') + '/.local/share/applications', ['halo.desktop']),
          (os.getenv('HOME') + '/.local/share/icons', ['halo/assets/halo.svg']),
      ],
      package_data={
          '': ['*.css', 'assets/*.*', 'assets/icon/*']
      },
      zip_safe=False)
