from setuptools import find_packages, setup

setup(
    name='jason-gnss',
    version_cc='{version}',
    author='Rokubun',
    author_email='info@rokubun.cat',
    description='Python bindings for Jason Positioning-as-a-Service: Rokubun GNSS processing engine in the cloud.',
    license='http://opensource.org/licenses/MIT',
    url="https://github.com/rokubun/jason-gnss",
    setup_requires=['setuptools-git-version-cc'],
    packages=["jason_gnss"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "docopt",
        "requests",
        "pytest"
    ],
    entry_points={
        'console_scripts': [
            'jason = jason_gnss.main:main'
        ]
    }
)

