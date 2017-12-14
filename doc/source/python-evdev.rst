Difference between libevdev-python and python-evdev
===================================================

python-evdev is an existing package that provides python access to the evdev
protocol. It's documentation is found here: https://python-evdev.readthedocs.io/en/latest/

They both wrap the same kernel protocol, so there is a large overlap
between the two projects.

The biggest difference and motivation for libevdev-python was that it wraps
libevdev rather than just using the kernel directly. This provides a number
of advantages, see **Why libevdev?** on the :doc:`index page <index>` for details.

From an API perspective, libevdev-python and python-evdev have two slightly
different approaches. For example,

* python-evdev opens the device directly and provides multiple ways of
  reading events from that device (using
  ``asyncore``, ``select``, ``selectors``, ``asyncio``, etc.).
  libevdev-python requires that the caller opens the file descriptor and
  monitors it, it merely pulls the events off when requested to do so.
* libevdev-python requires the conversion into `EventCode` and
  `EventType` early on, the rest of the API only deals with those.
  python-evdev largely sticks to integers instead (e.g. `dev.leds()` returns
  an integer array). This makes python-evdev less type-safe than
  libevdev-python.

There are other differences as well, but, unsurprisingly, we think that
libevdev-python is the better API and the safer choice. YMMV :)
