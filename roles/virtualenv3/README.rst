This roles allows to create a Python virtual environment with python3 instead of python2.7.

The role should be used with the following parameters:

``venv_user``
    The user under which the virtual environment is created

``venv_home_dir``
    ansible likes absolute paths in way too many places, the virtual
    environment is created in the users' home directory and this is its path

``venv_name``
    The name of the virtual environment

``venv_packages`` (default: empty list)
    packages to be installed using 'pkgng'

``venv_python_packages`` (default: empty list)
    Python packages to be installed using 'pip install'
