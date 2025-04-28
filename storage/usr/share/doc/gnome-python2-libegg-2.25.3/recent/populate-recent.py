import egg.recent
import sys
import os

def populate_from_directory(model, dirname, level):
    for root, dirs, files in os.walk(dirname):
        for name in files:
            model.add("file://%s" % os.path.join(root, name))
        level -= 1
        if level == 0:
            break

## unfortunately, we need a main loop to trigger notifications, so any
## modifications done through this tool won't be known to other apps

def main(argv):
    if len(argv) < 3:
        print "Usage:\n"
        print "populate-recent --add <URI>"
        print "populate-recent --delete <URI>"
        print "populate-recent --recurse-dir <directory> [<level>]"
        sys.exit(1)

    model = egg.recent.RecentModel(egg.recent.RECENT_MODEL_SORT_NONE)
    model.set_limit(0)

    if argv[1] == "--add":
        print "Adding: %s" % argv[2]
        model.add(argv[2])
    elif argv[1] == "--delete":
        print "Deleting: %s" % argv[2]
        model.delete(argv[2])
    elif argv[1] == "--recurse-dir":
        try:
            level = int(argv[3])
        except IndexError:
            level = 1
        print "Adding files from: %s" % argv[2]
        populate_from_directory(model, argv[2], level)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
