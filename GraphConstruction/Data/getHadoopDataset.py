from perceval.backends.core.mbox import MBox
# uri (label) for the mailing list to analyze
mbox_uri = 'http://mail-archives.apache.org/mod_mbox/hadoop-common-dev/'
# directory for letting Perceval know where mbox archives are
# you need to have the archives to analyzed there before running the script
mbox_dir = 'archives'

# create a mbox object, using mbox_uri as label, mbox_dir as directory to scan
repo = MBox(uri=mbox_uri, dirpath=mbox_dir)
# fetch all messages as an iteratoir, and iterate it printing each subject
for message in repo.fetch():
    print(message['data']['Subject'])