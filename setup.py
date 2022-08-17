from setuptools import setup, find_packages


setup(
    name='pyllicagram',
    version='1.4',
    license='Creative Commons',
    author="Benoit de Courson",
    author_email='b.decourson@csl.mpg.de',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/regicid/pyllicagram',
    keywords='example project',
    install_requires=[
          'pandas',
      ],

)
