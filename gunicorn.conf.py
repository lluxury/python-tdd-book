# Gunicorn configuration file for superlists project
# Usage: gunicorn --config gunicorn.conf superlists.wsgi:application

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync:gthread'
worker_connections = 1000
timeout = 30
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/superlists-access.log"
errorlog = "/var/log/gunicorn/superlists-error.log"
loglevel = "info"

# Process naming
proc_name = "superlists-[{procnum}]"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/superlists.pid"
umask = 0o007

# Server hooks
def on_starting(server, worker):
    """
    Just before the master process is initialized.
    """
    pass

def on_reload(server):
    """
    Called just before the master process is reloaded.
    """
    pass

def when_ready(server):
    """
    Called just after the server is ready to serve requests.
    """
    pass

def on_exit(server):
    """
    Called just before the master process is exited.
    """
    pass

# Django wsgi application
def when_ready(server):
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    server.log.info("Django application ready: %s" % application)
