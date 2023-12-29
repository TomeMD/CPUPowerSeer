from setuptools import setup, find_packages

setup(
    name='comets',
    version='0.1',
    description='CPU Power Modeling from Time Series.',
    author='Tomé Maseda',
    author_email='tome.maseda@udc.es',
    packages=find_packages(),
    install_requires=[
        'influxdb-client',
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'termcolor',
    ],
    entry_points={
        'console_scripts': [
            'comets = comets.main:main',
        ],
    },
)
