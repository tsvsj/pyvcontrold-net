from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md')

setup(
    name='pyvcontrold-net',
    description='A small library to interact with vcontrold (openv).',
    version='0.0.1',
    author='Sven Schaefer',
    author_email='tsvsjoj@gamil.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tsvsj/pyvcontrold',
    project_urls={
        'Bug Reports': 'https://github.com/tsvsj/pyvcontrold/issues',
        'Donating': 'https://www.buymeacoffee.com/tsvsj',
        'Say Thanks!': 'https://saythanks.io/to/tsvsj',
        'Source': 'https://github.com/tsvsj/pyvcontrold',
    },
    license='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: German',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='smarthome, vcontrold, openv, viessmann, heating control',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    install_requires=['PyYAML', 'Jinja2'],
)
