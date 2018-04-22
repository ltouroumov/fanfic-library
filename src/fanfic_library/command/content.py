from fanfic_library.command import default_registry, BaseCommand


@default_registry.register('update')
class UpdateCommand(BaseCommand):
    def build_parser(self, parser):
        parser.add_argument('fic_ids', default=0, nargs='*', type=int,
                            help="IDs of fanfics to update")
        parser.add_argument('--all', default=False, action='store_true', required=False,
                            help="Update ALL fanfics")

    def handle(self, args):
        session = self.setup(args)

        from fanfic_library.data import Fanfic
        from fanfic_library.operations import update_metadata

        if args.all:
            fics = session.query(Fanfic).order_by(Fanfic.title)
        else:
            fics = session.query(Fanfic).filter(Fanfic.id.in_(args.fic_ids))

        print("Updating fanfics:")
        for fic in fics:
            print("{id}: {title}".format(id=fic.id, title=fic.title))
            update_metadata(fic)


@default_registry.register('fetch')
class FetchCommand(BaseCommand):
    def build_parser(self, parser):
        parser.add_argument('fic_ids', default=0, nargs='*', type=int,
                            help="IDs of fanfics to update")
        parser.add_argument('--all', default=False, action='store_true', required=False,
                            help="Update ALL fanfics")

    def handle(self, args):
        session = self.setup(args)

        from fanfic_library.data import Fanfic
        from fanfic_library.operations import fetch_chapters

        if args.all:
            fics = session.query(Fanfic).order_by(Fanfic.title)
        else:
            fics = session.query(Fanfic).filter(Fanfic.id.in_(args.fic_ids))

        print("Fetching fanfics:")
        for fic in fics:
            print("{id}: {title}".format(id=fic.id, title=fic.title))
            fetch_chapters(fic)
