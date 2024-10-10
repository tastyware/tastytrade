Installation
============

Via pypi
--------

The easiest way to install tastytrade is using pip:

::

   $ pip install tastytrade

From source
-----------

You can also install from source.
Make sure you have `uv <https://docs.astral.sh/uv/getting-started/installation/>`_ installed beforehand.

::

   $ git clone https://github.com/tastyware/tastytrade.git
   $ cd tastytrade
   $ make install

If you're contributing, you'll want to run tests on your changes locally:

::

   $ make lint
   $ make test

If you want to build the documentation (usually not necessary):

::

   $ source .venv/bin/activate
   $ cd docs
   $ uv pip install -r requirements.txt
   $ make html

Windows
-------

If you want to install from source on Windows, you'll need to either use Cygwin/WSL, or run the commands from the Makefile manually.
Here's an example for PowerShell:

::

   $ git clone https://github.com/tastyware/tastytrade.git
   $ cd tastytrade
   $ uv sync
   $ uv pip install -e .
