from setuptools import setup, find_packages


setup(
    name='godaddy',
    version='2019.04.30',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'click',
        'requests',
    ],
    entry_points={
        'console_scripts': 'godaddy=godaddy:cli.main',
    },
)
