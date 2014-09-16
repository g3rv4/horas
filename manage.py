import sys
import peewee
from business_logic.models import *


def main(argv):
    if len(argv) == 1:
        print 'Command missing'
        sys.exit(1)

    if argv[1] == 'create_db':
        db.create_tables(peewee.Model.__subclasses__())
    elif argv[1] == 'create-company':
        print argv
        pass


if __name__ == "__main__":
    main(sys.argv)
