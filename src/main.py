import sys
from os import path

if __name__ == '__main__':
    src_path = path.dirname(__file__)
    sys.path.append(src_path)

    import fanfic_library
    fanfic_library.main()
