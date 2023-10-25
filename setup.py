import setuptools

setuptools.setup(
    name = 'cndr_stats',
    packages = setuptools.find_packages(),
    version = '0.2',
    license="MIT",
    description = 'Python routines for working with CNDR database tables',
    author = 'Paul A. Yushkevich <pyushkevich@gmail.com>',
    url = 'https://github.com/pyushkevich/cndr_stats',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'pandas', 
        'matplotlib', 
        'numpy',
        'openpyxl'
    ]
)