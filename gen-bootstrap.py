#!/usr/bin/env python
#
# Set up a virtualenv environment with the prerequisites for csrv.
# To use this, install virtualenv, run this script, and then run the generated
# csrv-bootstrap.py to create an environment with the needed dependencies.
#
import virtualenv

script = virtualenv.create_bootstrap_script('''

import os
import subprocess

def after_install(options, home_dir):
  etc = os.path.join(home_dir, 'etc')
  if not os.path.exists(etc):
    os.makedirs(etc)
  subprocess.call([
      join(home_dir, 'bin', 'pip'), 'install', 'tornado',
  ])

''')
with open('csrv-bootstrap.py', 'w') as script_file:
  script_file.write(script)
