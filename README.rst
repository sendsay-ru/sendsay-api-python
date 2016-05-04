===================
Sendsay API Python
===================

The client library to support Sendsay API.

Installation
===================

.. code-block:: shell

    pip install sendsay-api-python

Requirements
===================

* requests
* ndg-httpsclient

Usage
===================

Getting the instance of the SendsayAPI class
-------------------
.. code-block:: python

  from sendsay.api import SendsayAPI

    api = SendsayAPI(login='<YOUR_LOGIN>', sublogin='<YOUR_SUBLOGIN>', password='<YOUR_PASSWORD>')

Making a simple request
-------------------
.. code-block:: python

    response = api.request('sys.settings.get', list=['about.name'])

Making an async request
-------------------
.. code-block:: python

    response = api.request('issue.send', {
        'sendwhen': 'now',
        'letter': {
            'subject': "Subject",
            'from.name': "Tester",
            'from.email': "test@test.ru",
            'message': {
                'html': "Sendsay API client test message<hr>Hello!</a>"
            },
            'attaches': [
                api.attach_file("sample.jpg")
            ],
        },
        'relink' : 1,
        'users.list': "test1@test.ru\ntest2@test.ru",
        'group' : 'masssending',
    })

    # Your tracking function definition if you want to track

    def track_process(resp, status_msg):
        print('---- %s' % status_msg) # Print a status message for example

    # Waiting for the end of the process with status tracking

    result = api.track_wait(
        response,
        callback=track_process, # your tracking function (if necessary)
        retry_interval=5,
        max_attempts=100
    )
