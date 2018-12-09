import os

from setuptools import setup

setup(name='Halo',
      version='0.1.0',
      description='The weather app',
      author='Cijo Saju',
      author_email='hello@cijo.me',
      license='MIT',
      packages=['halo'],
      entry_points={
        "console_scripts": [
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
            "matplotlib"
      ],
      data_files=[
            (os.getenv('HOME') + '/.local/share/applications', ['halo.desktop']),
            (os.getenv('HOME') + '/.local/share/icons', ['halo/assets/halo.svg']),
      ],
      package_data={
            '': ['*.css', 'assets/*', 'assets/icon/*']
      },
      zip_safe=False)
