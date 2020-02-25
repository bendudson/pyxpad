from setuptools import setup

version='0.4.0'

setup(name='pyxpad',
      version=version,
      description='Data visualisation and analysis tool for IDAM',
      author='Ben Dudson',
      author_email='benjamin.dudson@york.ac.uk',
      maintainer='Peter Hill',
      maintainer_email='peter.hill@york.ac.uk',
      url='https://github.com/ZedThree/pyxpad/',
      download_url='https://github.com/ZedThree/pyxpad/archive/{0}.tar.gz'.format(version),
      license='GPL',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: X11 Applications :: Qt',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Scientific/Engineering :: Physics',
          'Topic :: Scientific/Engineering :: Visualization',
      ],
      packages=['pyxpad'],
      install_requires=['matplotlib>=3.1', 'numpy>=1.15', 'scipy>=1.4', 'Qt.py>=1.2', 'xdg>=4.0.1'],
      entry_points={
          'gui_scripts': [
              'pyxpad = pyxpad.__main__:main',
          ],
      },
)
