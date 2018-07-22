from setuptools import setup, find_packages

setup(name='phylotastic_services',
      version='0.1',
      description='Python package for phylotastic services',
      long_description='Python package for phylotastic services',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Bioinformatics :: Phylogenetic analysis',
      ],
      keywords='phylotastic treeoflife webservices',
      url='https://github.com/phylotastic/phylo_webservices',
      author='Abu Saleh Md Tayeen',
      author_email='abusalehmdtayeen@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'ete3>=3.0.0b35',
          'dendropy',
          'beautifulsoap4'
      ],
      include_package_data=False,
      zip_safe=False)
