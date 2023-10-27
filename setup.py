from setuptools import setup, find_packages

setup(
    name='cpu_power_model',
    version='0.1',
    description='Modeling CPU Energy Consumption from InfluxDB Time Series',
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
            'cpu-power-model = cpu_power_model.main:main',
        ],
    },
)
