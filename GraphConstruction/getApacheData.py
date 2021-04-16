from perceval.backends.core.mbox import MBox
from perceval.backend import BackendCommandArgumentParser
from perceval.utils import DEFAULT_DATETIME
from perceval.backends.core.mbox import (logger,
                                         MBox,
                                         MBoxCommand,
                                         MBoxArchive,
                                         MailingList)


def validate_message(repo, message):
    """Check if the given message has the mandatory fields"""

    # This check is "case insensitive" because we're
    # using 'CaseInsensitiveDict' from requests.structures
    # module to store the contents of a message.
    if repo.MESSAGE_ID_FIELD not in message:
        # logger.warning("Field 'Message-ID' not found in message %s; ignoring",
        #                message['unixfrom'])
        return False

    if not message[repo.MESSAGE_ID_FIELD]:
        # logger.warning("Field 'Message-ID' is empty in message %s; ignoring",
        #                message['unixfrom'])
        return False

    if repo.DATE_FIELD not in message:
        # logger.warning("Field 'Date' not found in message %s; ignoring",
        #                message['unixfrom'])
        return False

    if not message[repo.DATE_FIELD]:
        # logger.warning("Field 'Date' is empty in message %s; ignoring",
        #                message['unixfrom'])
        return False
    try:
        str_to_datetime(message[repo.DATE_FIELD])
    except InvalidDateError:
        # logger.warning("Invalid date %s in message %s; ignoring",
        #                message[repo.DATE_FIELD], message['unixfrom'])
        return False
    return True

# import warnings

# warnings.filterwarnings("error")

# files to write mail data
f1 = open('msgDetailsRawNoErr.txt', 'w')
f2 = open('msgEdges.txt', 'w')
f3 = open('nameAndEmail.txt', 'w')
f4 = open('msgIdAndSubject.txt', 'w')
errorFile = open('errors.txt', 'w')
# uri (label) for the mailing list to analyze
mbox_uri = 'http://mail-archives.apache.org/mod_mbox/httpd-dev/'
# directory for letting Perceval know where mbox archives are
# you need to have the archives to analyzed there before running the script
mbox_dir = 'archives'

# create a mbox object, using mbox_uri as label, mbox_dir as directory to scan
repo = MBox(uri=mbox_uri, dirpath=mbox_dir)

# fetch all messages as an iteratoir, and iterate it printing each subject
countMsg = 0
totalMsg = 0
startMsg = True

for message in repo.fetch():
    msgId = message['data']['Message-ID'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    # if not(validate_message(repo, message)):
    #     totalMsg += 1
    #     errorFile.write(str(message) + '\n')
    #     continue
    inRepTo = ''
    if 'In-Reply-To' in message['data'] and message['data']['In-Reply-To']:
        inRepTo = message['data']['In-Reply-To'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')

    From = message['data']['From'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    Date = message['data']['Date'].encode('utf8', 'surrogateescape').decode('utf8', 'replace')
    subject = ''
    if 'Subject' in message['data'] and message['data']['Subject']:
        subject = message['data']['Subject'].encode('utf8', 'surrogateescape')
        subject = subject.decode('utf8', 'replace')
    msgId = msgId.replace('\n', '')
    inRepTo = inRepTo.replace('\n', '')
    From = From.replace('\n', '')
    Date = Date.replace('\n', '')
    subject = subject.replace('\n', '')
    f1.write(msgId + '/\\' + inRepTo + '/\\' + From + '/\\' + Date + '\n')
    f3.write(From + '\n')
    f4.write(msgId + '/\\')
    f4.write(subject)
    f4.write('\n')
    countMsg += 1
    totalMsg += 1
    # if countMsg == 100:
    #   print(msgId + '/\\' + inRepTo + '/\\' + From + '/\\' + Date + '\n')
    #   print(From + '\n')
    #   print(msgId + '/\\' + subject + '\n')

print(countMsg, totalMsg)
f1.close()
f2.close()
f3.close()
f4.close()
