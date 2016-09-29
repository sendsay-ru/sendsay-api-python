===================
Sendsay API Python
===================

The client library to support Sendsay API.

Installation
===================

.. code-block:: shell

    pip install sendsay-api-python

Dependencies 
===================

* requests

If your Python version older than 2.7.9, the following packages are required to support TLS SNI certificate checking:

* ndg-httpsclient
* pyopenssl
* pyasn1


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

    # Calling with parameters as dict
    response = api.request('member.set', { 'email': 'test1k@test.ru', 'addr_type': 'email', 'if_exists': 'overwrite', 'newbie.confirm': 0, 'return_fresh_obj': 1 })

    # Or with parameters as kwargs if we don't have '.' in any parameter name
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
                'html': "Sendsay API client test message<hr>Hello!"
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

    # Waiting for the end of the process

    result = api.track_wait(
        response,
        callback=track_process, # your tracking function (if necessary)
        retry_interval=5,
        max_attempts=100
    )
