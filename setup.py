import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from codecs import open

if sys.version_info[:3] < (3, 0, 0):
    print("Requires Python 3 to run.")
    sys.exit(1)

with open("README.md", encoding="utf-8") as file:
    readme = file.read()

setup(
    name="git-pull",
    description="Parallelized web scraper for Github",
    long_description=readme,
    long_description_content_type="text/markdown",
    version="v1.0.4",
    packages=["git_pull"],
    include_package_data=True,
    python_requires=">=3",
    url="https://github.com/shobrook/git-pull",
    author="shobrook",
    author_email="shobrookj@gmail.com",
    # classifiers=[],
    install_requires=[],
    keywords=["scraper", "web-scraper", "github", "github-scraper", "github-api", "parallel"],
    license="MIT"
)
