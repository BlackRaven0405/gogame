gogame
======

An easy way to simulate and automize go-like programs.

Installing
----------

To install the library from PyPi, you can just run the following command:

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U gogame

    # Windows
    py -3 -m pip install -U gogame

To install from the development sources, do the following:

.. code:: sh

    $ git clone https://github.com/BlackRaven0405/gogame
    $ cd gogame
    $ python3 -m pip install -U .

Quick Example
-------------

.. code:: py

    import gogame


    class RandomPlayer(gogame.Player):
        def play(self):
            return self.playable_moves()[0]


    b = gogame.Board()
    p1 = RandomPlayer(name="John")
    p2 = RandomPlayer(name="Smith")
    b.join(p1)
    b.join(p2)
    winner = b.run_game()
    print(winner)

You can find more examples in the example directory.

Links
-----

- `Documentation <https://gogame.readthedocs.io/en/latest/>`_
- `Rules of go <https://en.wikipedia.org/wiki/Rules_of_Go>`_