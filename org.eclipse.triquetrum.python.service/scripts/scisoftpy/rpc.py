###
# Copyright 2011 Diamond Light Source Ltd.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

'''
Analysis RPC Package
'''

import os
if os.name == 'java':
    raise 'Jython is unsupported'

from scisoftpy.python import pyrpc as _rpc #@Reimport
from scisoftpy.python import pywrapper as _wrapper #@Reimport
from scisoftpy.python import pyflatten as _flatten #@Reimport

rpcserver=_rpc.rpcserver
rpcclient=_rpc.rpcclient
typednone=_wrapper.typednone
binarywrapper=_wrapper.binarywrapper
settemplocation=_flatten.settemplocation


if __name__ == '__main__':
    # When run as a script, launches an RPC Server
    import sys

    serverPort = int(sys.argv[1])
    server = rpcserver(serverPort)

    def addHandlers(code, handler_names):
        ''' Add new handlers to the running server.
            The code is 'exec'uted with custom dictionaries, the names
            in handler_names must be defined by code and then
            are added to the server
        '''
        # We run in the context of the rpc.py, however we must
        # give a __name__ other than __main__ so that a script
        # that has if ... __main__ does not run the main code
        g = dict(globals())
        g['__name__'] = '<addHandlerCode>'
        exec(code, g)
        for handler_name in handler_names:
            server.add_handler(handler_name, g[handler_name])
    server.add_handler('addHandlers', addHandlers)

    # Run the server's main loop
    server.serve_forever()
