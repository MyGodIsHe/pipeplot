Pipe Plot
=========

.. image:: https://img.shields.io/pypi/v/pipeplot.svg
    :target: https://pypi.org/project/pipeplot/

.. image:: https://img.shields.io/pypi/pyversions/pipeplot.svg
    :target: https://pypi.org/project/pipeplot/

.. image:: https://img.shields.io/pypi/dm/pipeplot.svg
    :target: https://pypi.python.org/pypi/pipeplot

pipeplot draws an interactive graph in a terminal based on data from pipe.

Installation
============

.. code-block:: bash

    pip install pipeplot


Examples of using
=================

Ping like gping:

.. code-block:: bash

    ping ya.ru | grep --line-buffered time | sed -u -e 's#.*time=\([^ ]*\).*#\1#' | pipeplot

Chart of deaths per minute from coronavirus:

.. code-block:: bash

    while true; do curl -s https://coronavirus-19-api.herokuapp.com/all | jq '.deaths'; sleep 60; done | pipeplot

Render graphite to console:

.. code-block:: bash

    while sleep 5; do curl -s 'http://graphite/render?target=my_app_rps_error&format=json&from=-5min&until=now' | jq -c '.[0].datapoints[-1]'; done | sed -u s/null/0/ | stdbuf -oL uniq | stdbuf -oL jq '.[0]' | pipeplot
