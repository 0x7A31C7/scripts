import subprocess
import atexit
from pathlib import Path

import aria2p

_aria_proc = None
_client = None

def enable_aria_rpc(aria_path='aria2c', port=6800, secret=''):
    global _aria_proc, _client
    rpc_secret = [f'--rpc-secret="{secret}"'] if secret else []
    _aria_proc = subprocess.Popen([aria_path, '--enable-rpc', f'--rpc-listen-port={port}'] + rpc_secret, 
                          stdout=subprocess.PIPE)

    _client = aria2p.Client(host="http://localhost", port=port, secret=secret)

    for line in iter(_aria_proc.stdout.readline, b''):
        if b'listening on TCP port' in line:
            print(f'Aria RPC server listening on TCP port {port}')
            return

def shutdown_aria_rpc():
    if _aria_proc:
        _aria_proc.kill()

atexit.register(shutdown_aria_rpc)

def download(urls, dest, connections_per_url=1, n_mirrors=None, daemon=True, resume=True, overwrite=False):
    aria = aria2p.API(_client)

    if isinstance(dest, str):
        dest = Path(dest)

    options = {
        'dir': str(dest.expanduser().resolve()),
        'max-connection-per-server': str(connections_per_url), 
        'split':, 'out':, , 'allow-overwrite':, 'auto-file-renaming', 'remove-control-file'
        }
    options['split'] = str(n_mirrors)
    
    if overwrite:
        options['allow-overwrite'] = 'true'
        options['auto-file-renaming'] = 'false'

    if not resume:
        options['remove-control-file'] = 'true'
        options['allow-overwrite'] = 'true'
        
    aria.add_uris(urls, options=options)
