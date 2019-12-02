from setuptools import setup

setup(name='cmtestrunner',
      version='0.3',
      description='custom test runner for API test',
      author='Tasin Nawaz',
      author_email='tasin.buet@gmail.com',
      license='CM',
      packages=['cmtestrunner'],
      install_requires=[
          'django==2.0.6',
          'djangorestframework==3.8.2'
      ],
      zip_safe=False)

