.. currentmodule:: gogame
.. gogame documentation master file, created by
   sphinx-quickstart on Thu Mar 31 12:28:16 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gogame's documentation!
===================================

Enums
~~~~~
.. autoclass:: Color

   :bool(color):
      Returns False if color is Empty, True otherwise

   .. attribute:: Empty

      The vertice is Empty
   .. attribute:: Black

      The vertice is owned by Black
   .. attribute:: White

      The vertice is owned by White
   .. attribute:: Green

      The vertice is owned by Green
   .. attribute:: Blue

      The vertice is owned by Blue
   .. attribute:: Yellow

      The vertice is owned by Yellow
   .. attribute:: Purple

      The vertice is owned by Purple
   .. attribute:: Wall

      The vertice is occupied by a Wall
   .. automethod:: Color.is_player

Player
~~~~~~
.. attributetable:: Player

.. autoclass:: Player
   :members:

Board
~~~~~
.. attributetable:: Board

.. autoclass:: Board
    :members:

Territory
~~~~~~~~~
.. attributetable:: Territory

.. autoclass:: Territory
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


