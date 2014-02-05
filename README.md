# Central Server

A card game of hacking and trickery

### Installation Setup
---

Clone the project repository and make sure you have [virtualenv][1]. Next enter the project directory and run the bootstrap script to generate a config file that you can then run to create the virtualenv environment.

    $ python gen-bootstrap.py
    $ python csrv-bootstrap.py .
    
Finally activate the virtualenv environment and then you can run the server or tests with the corresponding startup scripts.

    $ source bin/activate
    $ ./run_server
    $ ./run_tests

[1]: http://www.virtualenv.org/
