import argparse
from collections import OrderedDict
import importlib
from os import path


command_modules = (
    'fanfic_library.command.content',
    'fanfic_library.command.works',
)


def load_modules():
    for adapter in command_modules:
        importlib.import_module(adapter)


class CommandRegistry:
    def __init__(self):
        self.handlers = OrderedDict()

    def register(self, subcommand):
        def decorator(cls):
            self.handlers[subcommand] = cls

        return decorator


default_registry = CommandRegistry()


class CommandHander:
    def __init__(self, registry, sub_cmd_arg='sub_cmd'):
        self.registry = registry
        self.handlers = OrderedDict()
        self.parser = None
        self.sub_cmd_arg = sub_cmd_arg

    def build(self, parent=None):
        if parent is None:
            parser = argparse.ArgumentParser(description="Fanfic Library command line tool")
            parser.add_argument('--workdir', help="Working Directory", default='.', type=path.realpath)
        else:
            parser = parent

        subp = parser.add_subparsers(dest=self.sub_cmd_arg)

        for subcmd, cls in self.registry.handlers.items():
            handler = cls()
            handler.build_parser(subp.add_parser(subcmd))
            self.handlers[subcmd] = handler

        self.parser = parser

    def run(self, override_args=None):
        if override_args:
            args = override_args
        else:
            args = self.parser.parse_args()

        sub_cmd = getattr(args, self.sub_cmd_arg)
        if sub_cmd in self.handlers:
            handler = self.handlers[sub_cmd]
            try:
                handler.handle(args)
            except KeyboardInterrupt:
                print("Terminated!")
            except:
                import traceback
                traceback.print_exc()
        elif sub_cmd is None:
            self.parser.print_help()
        else:
            print("Unkown subcommand", sub_cmd)


class BaseCommand:
    def build_parser(self, parser):
        pass

    def setup(self, args):
        from fanfic_library import build_env
        from fanfic_library.data import session
        workdir, db_engine = build_env(args.workdir)
        session.configure(bind=db_engine)

        return session

    def handle(self, args):
        raise NotImplementedError('handle')


@default_registry.register('setup')
class SetupCommand(BaseCommand):
    def handle(self, args):
        from fanfic_library import build_env
        workdir, db_engine = build_env(args.workdir)

        from fanfic_library.data import Base
        Base.metadata.create_all(db_engine)


@default_registry.register('ui')
class WebUiCommand(BaseCommand):
    def build_parser(self, parser):
        from fanfic_library import DEBUG_MODE

        parser.add_argument('--host', dest='host', default='localhost',
                            help="Listen on host")
        parser.add_argument('--port', dest='port', default=8080,
                            help="Listen on port")
        parser.add_argument('--debug', dest='debug', action='store_true', default=DEBUG_MODE,
                            help="Start in debug mode")

    def handle(self, args):
        from fanfic_library import build_env
        from fanfic_library.webui import app
        from fanfic_library.data import session
        workdir, db_engine = build_env(args.workdir)
        session.configure(bind=db_engine)
        app.run(args.host, args.port, args.debug)