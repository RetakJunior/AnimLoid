from setuptools import setup, find_packages

setup(
    name="animloid",
    version="2.7.0",
    packages=find_packages(include=["weeb_cli", "weeb_cli.*"]),
    package_data={"weeb_cli": ["locales/*.json", "templates/*.html"]},
    py_modules=["weeb_app_entry"],
    entry_points={
        "console_scripts": [
            "animloid=weeb_app_entry:main",
        ],
    },
    install_requires=[
        "typer[all]", "rich", "questionary", "requests",
        "packaging", "beautifulsoup4", "lxml", "pycryptodome",
        "curl_cffi", "appdirs", "pyfiglet", "py7zr", "pypresence",
    ],
)
