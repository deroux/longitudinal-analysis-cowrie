from setuptools import find_packages
from setuptools import setup

setup(
    name='longitudinal-analysis-cowrie',
    version='1.0.0',
    url='https://github.com/deroux/longitudinal-analysis-cowrie',
    license='MIT',
    author='deroux',
    author_email='dominicrudigier@gmail.com',
    description='Longitudinal Analysis of SSH Cowrie Honeypots',
    install_requires=['click', 'pyfiglet', 'tqdm', 'orjson', 'tabulate', 'rich', 'plotly', 'paramiko'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cowralyze = cowralyze.cowralyze:cli',
        ]
    }

)
