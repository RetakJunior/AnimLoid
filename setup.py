from setuptools import setup, find_packages

setup(
    name="animloid",
    version="2.7.3",
    license="GPL-3.0-only",
    packages=find_packages(include=["weeb_cli", "weeb_cli.*"]),
    package_data={"weeb_cli": ["locales/*.json", "templates/*.html"]},
    py_modules=["weeb_app_entry", "gui_main"],
    entry_points={
        "console_scripts": [
            "animloid=weeb_app_entry:main",
        ],
    },
    install_requires=[
        "typer[all]", "rich", "questionary", "requests",
        "packaging", "beautifulsoup4", "lxml", "pycryptodome",
        "curl_cffi>=0.8.1,<0.9; python_version < '3.9'",
        "curl_cffi>=0.10,<0.14; python_version >= '3.9' and python_version < '3.10'",
        "curl_cffi>=0.14; python_version >= '3.10'",
        "appdirs", "pyfiglet", "py7zr", "pypresence", "PyQt5>=5.15.0",
    ],
)
