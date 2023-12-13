from setuptools import setup, find_packages

readme = open('README.rst').read()

setup(
    name='xetcache',
    version='0.0.2',
    description='An extension for IPython that help to run AsyncIO code in '
                'your interactive session.',
    long_description=readme,
    author='Yucheng Low',
    author_email='ylow@xethub.com',
    url='https://github.com/xetdata/xetcache',
    packages=find_packages(),
    install_requires=(
        'ipython', 'pyxet', 'fsspec'
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: IPython',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
