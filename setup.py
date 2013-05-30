from setuptools import setup, find_packages
from mezzanine_recipes import __version__

setup(
    name='mezzanine-beer-recipes',
    version=__version__,
    author='Andrea Rossi',
    author_email='direlemming+github@gmail.com',
    description='Beers Recipe blog posts for Mezzanine CMS',
    url='https://github.com/RossiAndrea/mezzanine-beer-recipes',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'setuptools_git>=0.3',
    ],
    install_requires=[
        'Mezzanine>=1.3.0',
        'django-tastypie>=0.9.12-alpha',
        'South>=0.7.6',
        'uuid>=1.30',
    ],
    # dependency_links = [
    #     'http://github.com/toastdriven/django-tastypie/tarball/master#egg=django-tastypie-0.9.12-alpha',
    # ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
