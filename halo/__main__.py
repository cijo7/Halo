import sys

from halo.app import Halo


def main():
    app = Halo()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)


if __name__ == '__main__':
    main()
