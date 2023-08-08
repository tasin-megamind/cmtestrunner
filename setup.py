import setuptools

setuptools.setup(name='cmtestrunner',
      version='2.2.11',
      description='custom test runner for API test',
      author='Tasin Nawaz',
      author_email='tasin.buet@gmail.com',
      license='CM',
      url='https://github.com/tasin-megamind/cmtestrunner',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
          'django',
          'djangorestframework',
          'PyYAML',
          'requests',
          'case-insensitive-dictionary'
      ],
      zip_safe=False)

