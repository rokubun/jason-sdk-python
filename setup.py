from setuptools import find_packages, setup

setup(
    name='jason-gnss',
    version_cc='{version}',
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

