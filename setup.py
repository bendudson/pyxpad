from setuptools import setup

setup(name='pyxpad',
      version='0.1.0',
      description='Data visualisation and analysis tool for IDAM',
      author='Ben Dudson',
      author_email='benjamin.dudson@york.ac.uk',
      url='https://github.com/ZedThree/pyxpad/',
      download_url='https://github.com/ZedThree/pyxpad/tarball/0.1.0',
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
      install_requires=['matplotlib', 'numpy', 'scipy', 'PySide', 'xdg'],
      entry_points={
          'gui_scripts': [
              'pyxpad = pyxpad.__main__:main',
          ],
      },
)
