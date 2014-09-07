try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'EnsiColab',
	'author': 'Raphael Gontijo Lopes',
	'url': 'Not available',
	'download_url': 'Not available',
	'author_email': 'raphaelgontijolopes@gmail.com',
	'version': '0.1',
	'install_requires': ['nose', 'hashlib'],
	'packages': ['EnsiColab'],
	'scripts': [],
	'name': 'EnsiColab'
}

setup(**config)
