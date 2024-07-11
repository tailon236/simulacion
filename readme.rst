N-Body Simulator
================

This simulates the gravitational interaction of a bunch of stars
using Python and GLSL.
It is an "N-Body simulator".
By using the GPU, it is reasonably performant compared to a CPU-only version.

.. image:: screenshots/screenshot.png

The simulator uses/depends on:

* Python 3.7 - 3.9 (Not 3.10 because of a shapely library dependency)
* Compute Shaders (Needs OpenGL 4.3+)
* Arcade Library

A longer tutorial is available on the
`Arcade website <https://api.arcade.academy/en/development/tutorials/compute_shader/index.html>`_.

You can adjust the ``num_stars`` parameter if your hardware is running this too slow.
There are a couple different initial star setups you can try.

.. figure:: screenshots/galaxies.png

   gen_galaxies_colliding function


.. figure:: screenshots/gen_random_space.png

   gen_random_space function
