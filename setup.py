from setuptools import setup, find_packages

version_file = open('crawler/version.py')
version = version_file.read().split('=')[1].strip()[1:-1]

with open('requirements.txt') as f:
    required = f.read().splitlines()


with open('README.md') as f:
    readme = f.read()

setup(
	name = 'url_crawling',
	version = version,
	packages = ['crawler'],
	install_requires=required,
	long_description = readme,
	long_description_content_type = 'text/markdown',
	test_suite = 'tests'
)