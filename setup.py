from pathlib import Path

from setuptools import (find_packages,
                        setup)

import gon

project_base_url = 'https://github.com/lycantropos/gon/'

setup(name=gon.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=gon.__version__,
      description=gon.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      install_requires=Path('requirements.txt').read_text())
