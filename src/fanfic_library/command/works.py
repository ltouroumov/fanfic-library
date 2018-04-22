from fanfic_library.command import default_registry, CommandRegistry, CommandHander, BaseCommand


work_registry = CommandRegistry()


@default_registry.register('works')
class WorksCommand(BaseCommand):
    def __init__(self):
        self.handler = CommandHander(work_registry, sub_cmd_arg='work_cmd')

    def build_parser(self, parser):
        self.handler.build(parent=parser)

    def handle(self, args):
        print("Works!")
        self.handler.run(override_args=args)


@work_registry.register('list')
class ListCommand(BaseCommand):
    def build_parser(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--by-title', dest='sort', action='store_const', const='title',
                           help="Sort results by title (A-Z)")
        group.add_argument('--by-word-count', dest='sort', action='store_const', const='word-count',
                           help="Sort results by word count (descending)")
        group.add_argument('--by-author', dest='sort', action='store_const', const='author',
                           help="Sort results by author (A-Z)")

        parser.add_argument('--search', default=None,
                            help="Search in title and author")

        parser.add_argument('--limit', default=0, type=int)

    def handle(self, args):
        session = self.setup(args)

        from tabulate import tabulate
        from fanfic_library.data import Fanfic
        from fanfic_library.utils import format_word_count

        fics = session.query(Fanfic)

        if args.search:
            search = args.search
            fics = fics.filter(Fanfic.title.contains(search) | Fanfic.author.contains(search))

        if args.sort == 'title':
            fics = fics.order_by(Fanfic.title)
        elif args.sort == 'author':
            fics = fics.order_by(Fanfic.author)
        elif args.sort == 'word-count':
            fics = fics.order_by(Fanfic.words.desc())
        else:
            fics = fics.order_by(Fanfic.id)

        if args.limit > 0:
            fics = fics.limit(args.limit)

        print(tabulate(((fic.id, fic.title, fic.author, format_word_count(fic.words)) for fic in fics),
              headers=('ID', 'Title', 'Author', 'Word Count')))


@work_registry.register('add')
class AddCommand(BaseCommand):
    def build_parser(self, parser):
        parser.add_argument('thread_urls', nargs='*',
                            help="URLs to add")
        parser.add_argument('--from', dest='from_file',
                            help="Read URLs from file")

    def handle(self, args):
        if args.from_file:
            with open(args.from_file, mode="r") as fd:
                thread_urls = map(str.strip, fd.readlines())
        else:
            thread_urls = args.thread_urls

        from fanfic_library.operations import create_from_thread_url

        for thread_url in thread_urls:
            print("Adding", thread_url)
            new, fic = create_from_thread_url(thread_url)
            if new:
                print("Added", fic.title)
            else:
                print("Updated", fic.title)

            print()


@work_registry.register('del')
class AddCommand(BaseCommand):
    def handle(self, args):
        print("Remove a work")
