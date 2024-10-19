import multiprocessing

bind = "127.0.0.1:30720"
workers = 2
threads = 2
accesslog = "/home/model/apps/tournaments/gunicorn.log"
pidfile = "/home/model/apps/tournaments/tmp/tournaments.pid"
reload = True
