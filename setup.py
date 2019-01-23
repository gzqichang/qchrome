from setuptools import setup, find_packages

setup(
    name="qchrome",
    author="gzqichang",
    version="0.1",
    packages=find_packages(),
    # include_package_data=True,
    zip_safe=False,
    package_data={
        '': ['*.html', '*.css', '*.js', '*.config']
    },
    install_requires=[
        'requests',
        'websocket-client',
    ],
    dependency_links=[
    ],
)
