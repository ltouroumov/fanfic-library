from os import path
import os

DEBUG_MODE = bool(os.getenv('DEBUG', 0))


def build_env(workdir):
    from sqlalchemy import create_engine

    db_file = path.join(workdir, 'data.db')
    db_engine = create_engine("sqlite:///%s" % db_file, echo=DEBUG_MODE)

    from fanfic_library import cache, adapter

    cache.http.setup(path.join(workdir, 'cache'))
    cache.thread.setup(workdir)

    adapter.load_all()

    return workdir, db_engine


def main():
    from fanfic_library.command import load_modules, default_registry, CommandHander

    load_modules()

    handler = CommandHander(default_registry)
    handler.build()
    handler.run()


if __name__ == '__main__':
    main()
