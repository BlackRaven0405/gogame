gopy
====

An easy way to simulate and automize go-like programs.

Installing
----------

Coming soon on PyPi

--------------------------

To install from the development sources, do the following:

.. code:: sh

    $ git clone https://github.com/BlackRaven0405/gopy
    $ cd gopy
    $ $ python3 -m pip install -U .

Quick Example
-------------

.. code:: py

    import gopy


    class RandomPlayer(gopy.Player):
        def play(self):
            return self.playable_moves()[0]


    b = gopy.Board()
    p1 = RandomPlayer(name="John")
    p2 = RandomPlayer(name="Smith")
    b.join(p1)
    b.join(p2)
    winner = b.run_game()
    print(winner)

You can find more examples in the example directory.

Links
-----

- Documentation (coming soon)
- `Rules of go <https://en.wikipedia.org/wiki/Rules_of_Go>`_