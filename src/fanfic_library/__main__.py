import argparse
import sys
from os import path
import os
from fanfic_library import cache, adapter

DEBUG_MODE = bool(os.getenv('DEBUG', 0))


def build_env(workdir):
    from sqlalchemy import create_engine

    db_file = path.join(workdir, 'data.db')
    db_engine = create_engine("sqlite:///%s" % db_file, echo=DEBUG_MODE)

    cache.http.setup(path.join(workdir, 'cache'))
    cache.thread.setup(workdir)

    adapter.load_all()

    return workdir, db_engine


def main():
    parser = argparse.ArgumentParser(description="Fanfic Library command line tool")
    parser.add_argument('--workdir', help="Working Directory", default='.', type=path.realpath)

    subp = parser.add_subparsers(dest='subcmd')

    webui = subp.add_parser('ui')
    webui.add_argument('--host', dest='host', default='localhost',
                       help="Listen on host")
    webui.add_argument('--port', dest='port', default=8080,
                       help="Listen on port")
    webui.add_argument('--debug', dest='debug', action='store_true', default=DEBUG_MODE,
                       help="Start in debug mode")

    subp.add_parser('setup')

    args = parser.parse_args()

    if args.subcmd == 'ui':
        from fanfic_library.webui import app
        from fanfic_library.data import session

        workdir, db_engine = build_env(args.workdir)
        session.configure(bind=db_engine)

        app.run(args.host, args.port, args.debug)
    elif args.subcmd == 'setup':
        workdir, db_engine = build_env(args.workdir)
        from fanfic_library.data import Base

        Base.metadata.create_all(db_engine)
    else:
        print("Unkown subcommand", file=sys.stderr)


if __name__ == '__main__':
    main()
