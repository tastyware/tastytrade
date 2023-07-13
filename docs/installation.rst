Installation
============

Via pypi
--------

The easiest way to install tastytrade is using pip:

::

   $ pip install tastytrade

From source
-----------

You can also install from source:

::

   $ git clone https://github.com/tastyware/tastytrade.git
   $ cd tastytrade; make venv
   $ source env/bin/activate
   $ make install

If you're contributing, you'll want to run tests on your changes locally:

::

   $ make test

And finally, to build the documentation:

::

   $ make docs

The first time, you'll need to install the documentation dependencies:

::

   $ pip install -r docs/requirements.txt

Windows
-------

If you want to install from source on Windows, you'll need to either use Cygwin/WSL, or run the commands from the Makefile manually.
Here's an example for PowerShell:

::

   $ git clone https://github.com/tastyware/tastytrade.git
   $ cd tastytrade
   $ python -m venv env
   $ env/Scripts/Activate.ps1
   $ env/Scripts/pip.exe install -r requirements.txt
   $ env/Scripts/pip.exe install -e .
