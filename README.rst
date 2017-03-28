===================
Sendsay API Python
===================

The client library to support Sendsay API.

Please note that the current version of the package is not backward compatible with the versions before v1.0.0.

* API request returns an instance of ``Response`` instead of dict
* ``track_wait`` was removed from ``SendsayAPI`` class. You can get the tracking information by using
  ``track`` method of a response returned
* ``attach_file`` is a method of ``sendsay.api`` module



Installation
============

.. code-block:: shell

    pip install sendsay-api-python

Dependencies 
============

* ``requests``

If your Python version older than 2.7.9, the following packages are required to support TLS SNI certificate checking:

* ``ndg-httpsclient``
* ``pyopenssl``
* ``pyasn1``


Usage
=====

Getting an instance of the SendsayAPI class
-------------------------------------------
.. code-block:: python

  from sendsay.api import SendsayAPI

    api = SendsayAPI(login='<YOUR_LOGIN>', sublogin='<YOUR_SUBLOGIN>', password='<YOUR_PASSWORD>')

Making a simple request
-----------------------

.. code-block:: python

    # Calling with parameters
    response = api.request('member.set', { 'email': 'test1k@test.ru', 'addr_type': 'email', 'if_exists': 'overwrite', 'newbie.confirm': 0, 'return_fresh_obj': 1 })

    # Getting the response data

    response = api.request('sys.settings.get', dict(list=['about.name']))
    print(response.data)


Making an async request and track the result
--------------------------------------------
.. code-block:: python

    from sendsay.api import SendsayAPI, attach_file
    from time import sleep

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
                attach_file("sample.jpg")
            ],
        },
        'relink' : 1,
        'users.list': "test1@test.ru\ntest2@test.ru",
        'group' : 'masssending',
    })

    # If the response has tracking data
    if response.track:
        # Refresh the tracking status
        while response.track.check():
            # Get the current status
            print(response.track.status, response.track.status_message)
            sleep(3)
