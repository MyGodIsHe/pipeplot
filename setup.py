from setuptools import setup
import codecs


# Copied from (and hacked):
# https://github.com/pypa/virtualenv/blob/develop/setup.py#L42
def get_version(filename):
    import os
    import re

    here = os.path.dirname(os.path.abspath(__file__))
    f = codecs.open(os.path.join(here, filename), encoding='utf-8')
    version_file = f.read()
    f.close()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(
    name='pipeplot',
    description='displays an interactive graph based on data from pipe',
    long_description=long_description,
    version=get_version('pipeplot.py'),
    license='MIT',
    author='Ilya Chistyakov',
    author_email='ilchistyakov@gmail.com',
    py_modules=['pipeplot'],
    entry_points={
        'console_scripts': ['pipeplot=pipeplot:run'],
    },
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    url='https://github.com/MyGodIsHe/pipeplot',
    project_urls={
        'Source': 'https://github.com/MyGodIsHe/pipeplot',
    },
)
