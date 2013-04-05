from distutils.core import setup
from swiftst import __version__ as version

name = "swift-setuptools"

install_requires = []
try:
    import fabric
except ImportError:
    install_requires.append("fabric")

data_files = [('/etc/swift-setuptools',
               ['etc/swift-setuptools.conf-sample']),
              ('/etc/swift-setuptools/templates',
               ['templates/*'])]

setup(
    name = name,
    version = version,
    author = "Joao Marcelo Martins",
    author_email = "btorch@gmail.com",
    description = "Help scripts to setup a swift cluster",
    license = "Apache License, (2.0)",
    keywords = "openstack swift",
    url = "https://github.com/btorch/swift-setuptools",
    packages=['swiftst'],
    classifiers=[
        'Development Status :: 1 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        ],
    install_requires=install_requires,
    scripts=['bin/swift-node-setup',
             'bin/swift-genconfigs',
             'bin/swift-admin-setup',],
    data_files = data_files)
