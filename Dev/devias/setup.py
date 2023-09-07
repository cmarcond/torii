from setuptools import setup, find_packages

setup(
    name='devias',
    version='0.1',
    packages=['paginas_iniciais'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)