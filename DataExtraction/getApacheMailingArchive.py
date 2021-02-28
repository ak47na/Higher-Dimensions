from perceval.backends.core.mbox import MBox

# files to write mail data
f1 = open('msgDetails.txt', 'w')
f2 = open('msgEdges.txt', 'w')
f3 = open('nameAndEmail.txt', 'w')
f4 = open('msgIdAndSubject.txt', 'w')
# uri (label) for the mailing list to analyze
mbox_uri = 'http://mail-archives.apache.org/mod_mbox/httpd-dev/'
# directory for letting Perceval know where mbox archives are
# you need to have the archives to analyzed there before running the script
mbox_dir = 'archives'

# create a mbox object, using mbox_uri as label, mbox_dir as directory to scan
repo = MBox(uri=mbox_uri, dirpath=mbox_dir)

# fetch all messages as an iteratoir, and iterate it printing each subject
countMsg = 0
for message in repo.fetch():
    msgId = message['data']['Message-ID'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    inRepTo = 'None'
    if 'In-Reply-To' in message['data'] and message['data']['In-Reply-To']:
        inRepTo = message['data']['In-Reply-To'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')

    From = message['data']['From'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    Date = message['data']['Date'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    subject = 'None'
    if 'Subject' in message['data'] and message['data']['Subject']:
        subject = message['data']['Subject'].encode('utf8', 'surrogateescape')
        subject = subject.decode('utf8', 'replace')
    f1.write(msgId + '/\\' + inRepTo + '/\\' + From + '/\\' + Date + '\n')
    f3.write(From + '\n')
    f4.write(msgId + '/\\')
    f4.write(subject)
    f4.write('\n')
    countMsg += 1
    if countMsg == 100:
        print(msgId + '/\\' + inRepTo + '/\\' + From + '/\\' + Date + '\n')
        print(From + '\n')
        print(msgId + '/\\' + subject + '\n')

print(countMsg)
f1.close()
f2.close()
f3.close()
f4.close()
