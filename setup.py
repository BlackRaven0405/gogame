from setuptools import setup
import re

version = ''
with open('gopy/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README.rst') as f:
    readme = f.read()

setup(
    name='gopy',
    version=version,
    license='MIT',
    description='An easy way to simulate and automize go-like programs.',
    long_description=readme,
    long_description_content_type="text/x-rst",
    author="BlackRaven0405",
    author_email='ljouhault@crowbots.shop',
    packages=['gopy'],
    url='https://github.com/BlackRaven0405/gopy',
    keywords='go gopy',
    python_requires='>=3',
    install_requires=[
          'numpy',
      ],

)