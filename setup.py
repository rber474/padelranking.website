from setuptools import find_packages, setup

setup(
    name='paddelranking.website',
    description='A short description',
    version='1.0.0',
    author='Rafael Bermudez Horcajada',
    author_email='rber474@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)


