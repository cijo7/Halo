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


setup(name='halo-weather',
      version=VERSION,
      description='The weather app.',
      long_description=get_long_description(),
      author='Cijo Saju',
      author_email='halo@cijo.mni.im',
      license='MIT',
      packages=['halo'],
      url='https://github.com/cijo7/Halo',
      entry_points={
          "gui_scripts": [
              "halo-weather = halo.__main__:main",
          ]
      },
      install_requires=[
          "requests",
          "pytz",
          "pygobject",
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
