=======================================
MicroDonuts: An OpenTracing Walkthrough
=======================================


Welcome to MicroDonuts! This is a sample application and OpenTracing
walkthrough, written in Python.

OpenTracing is a vendor-neutral, open standard for distributed tracing. To
learn more, check out [opentracing.io](http://opentracing.io), and try the
walkthrough below!

**Note that there are two git branches of note here.**
- `git checkout master` illustrates a trivial multi-service app with cross-service tracing via OpenTracing
- `git checkout no-tracing` removes the tracing instrumentation, allowing the reader to add it in themselves

Step 0: Setup MicroDonuts
=========================

Getting it
----------

#. Install `virtualenv`: `sudo -H pip3 install virtualenv`
#. Create a virtual environment: `mkdir microdonuts; virtualenv microdonuts`
#. Activate the virtual environment: `source microdonuts/bin/activate`
#. Clone this repository
#. Install the dependencies `pip3 install -r python-opentelemetry-walkthrough/requirements.txt`

Running
-------

#. `pyhton3 python-opentelemetry-walkthrough/walkthrough/server.py`
#. Open your web browser, navigate to `http://127.0.0.1:10001` and order yourself some µ-donuts.

MicroDonuts has 4 server endpoints:

#. `/order`
#. `/status`
#. `/kitchen/add_donuts`
#. `/kitchen/get_donuts`

The first 2 serve orders, the last 2 provide kitchen services.

Step 1: Check out the `no-tracing` branch
-----------------------------------------

The `master` branch in this repository has tracing instrumentation added as
described below. To maximize your learnings, do a...

.. code:: bash

    git checkout no-tracing

...to start with a version of the code that's not instrumented yet. The guide
below will let you learn-by-doing as you re-introduce that tracing
instrumentation.

Step 2: Turnkey Tracing
-----------------------

When you go to add tracing to a system, the best place to start is by
installing OpenTracing plugins for the OSS components you are using.
Instrumenting your networking libraries, web frameworks, and service clients
quickly gives you a lot of information about your distributed system, without
requiring you to change a lot of code.

To do this, let's change the startup of the application to include tracing:
`cd python-opentelemetry-walkthrough/walkthrough`

Start the global tracer
.......................

In OpenTracing, there is a concept of a global tracer for everyone to access.

Accessing this global tracer is easy, just add these lines to `server.py` under
`BLOCK 0`:

.. code:: python

    from opentelemetry import trace, propagators
    from opentelemetry.sdk.trace import Tracer
    from opentelemetry.sdk.context.propagation.b3_format import B3Format

Add these lines under `BLOCK 1` too:

.. code:: python

    trace.set_preferred_tracer_implementation(lambda T: Tracer())

    propagators.set_global_httptextformat(B3Format())

    tracer = trace.tracer()

The global tracer is now available as `tracer`.


Instrument the HTTP requests
............................

This is done in an automatic way by just adding this line under `BLOCK 0`:

.. code:: python

    from opentelemetry.ext.http_requests import enable

Add also this line under `BLOCK 1`:

.. code:: python

    enable(tracer)

Instrument Flask
................

This example uses Flask to expose the HTTP endpoints. Flask code can
be traced automatically by adding this line under `BLOCK 0`:

.. code:: python

    from opentelemetry.ext.wsgi import OpenTelemetryMiddleware

Add this line under `BLOCK 2` also:

.. code:: python

    app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)

Add an exporter
...............

An exporter is necessary for the span data to be displayed. We'll use the
`ConsoleExporter` in this example, an exporter that simply prints the span data
into the console. Add these lines under `BLOCK 0`:

.. code:: python

    from opentelemetry.sdk.trace.export import ConsoleSpanExporter
    from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

Add this line under `BLOCK 1`:

.. code:: python

    tracer.add_span_processor(
        SimpleExportSpanProcessor(ConsoleSpanExporter())
    )


Step 3: Have fun
----------------

You can run the walkthrough again as explained before. You should see the span
data displayed in the console.

Thanks for playing, and welcome to OpenTelemetry!

Thanks for joining us in this walkthrough! Hope you enjoyed it. If you did, let
us know, and consider spreading the love!

*Aloha!*
