import setuptools

setuptools.setup(name='cmtestrunner',
      version='0.9',
      description='custom test runner for API test',
      author='Tasin Nawaz',
      author_email='tasin.buet@gmail.com',
      license='CM',
      url='https://github.com/tasin-megamind/cmtestrunner',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
          'django==2.0.6',
          'djangorestframework==3.8.2'
      ],
      zip_safe=False)

