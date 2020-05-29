#cmd += "eval `ssh-agent`" + "\n" + "ssh-add C:\\Users\\Maria\\firstKey.txt" + "\n"


import datetime
from perceval.backends.core.gerrit import Gerrit

# hostname of the Gerrit instance
hostname = 'git.eclipse.org'
# user for sshing to the Gerrit instance
user = 'akapros'

file1 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReviewEdges2020.txt", "w")
file2 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\UploaderNames2020.txt", "w")
file3 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\OwnerNames2020.txt", "w")
file4 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\CommentRevNames2020.txt", "w")
file5 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ApproverNames2020.txt", "w")
file6 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\AuthorNames2020.txt", "w")
file8 = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReviewFilesFromComments.txt", "w")
reviewData = open("D:\\Ak_work2019-2020\\HigherDimensions\\TxtDataInUse\\ReviewData.txt", "w")

repo = Gerrit(hostname=hostname, user=user)
uploaderNames = {}
authorNames = {}
ownerNames = {}
commentRevNames = {}
approverNames = {}
uploaderIdx = 0
authorIdx = 0
ownerIdx = 0
commentRevIdx = 0
approverIdx = 0
dateN = datetime.datetime(2020, 1, 1, 0, 0)
def Str(elem):
    return str(elem).encode("utf-8").decode()

for review in repo.fetch(from_date=dateN):
    if not(str(review['data']['project']) == 'jdt/eclipse.jdt.core'):
        continue
    reviewData.write(Str(review['data']['number']) + '/\\' + Str(review['data']['id']) + '/\\' + Str(review['data']['subject']) + '/\\' +
                     Str(review['updated_on']) + '/\\' + Str(review['data']['status']) + '\n')
    ownerName = Str(review['data']['owner']['name'])
    for patch in review['data']['patchSets']:
        name = Str(patch['author']['name'])
        revId = Str(patch['revision'])
        file1.write("AuthorEdge" + "/\\" + revId + "/\\" + name + "\n")
        if name != None and (not(name in authorNames)):
            authorIdx += 1
            authorNames[name] = authorIdx
        name = Str(patch['uploader']['name'])
        file1.write('Review2Commit/\\' + Str(review['data']['number']) + '/\\' + revId + "\n")
        file1.write("UploaderEdge" + "/\\" + revId + "/\\" + name + "\n")
        if name != None and (not (name in uploaderNames)):
            uploaderIdx += 1
            uploaderNames[name] = uploaderIdx
        if 'approvals' in patch:
            for approval in patch['approvals']:
                name = Str(approval['by']['name'])
                file1.write("ApprovalEdge/\\" + revId + "/\\" + name + "\n")
                if name != None and (not (name in approverNames)):
                    approverIdx += 1
                    approverNames[name] = approverIdx

        file1.write("OwnerEdge" + "/\\" + revId + "/\\" + ownerName + "\n")
        if 'comments' in patch:
            for comment in patch['comments']:
                if not ('reviewer' in comment) or not('name' in comment['reviewer']):
                    continue
                nameC = Str(comment['reviewer']['name'])
                if ownerName != nameC:
                    file1.write("PCommentEdge" + "/\\" + ownerName + "/\\" + nameC + "\n")
                if not (nameC in commentRevNames):
                    commentRevIdx += 1
                    commentRevNames[nameC] = commentRevIdx

                if 'file' in comment:
                    fileName = Str(comment['file'])
                    file8.write("CommentFileRelation/\\" + fileName + "/\\" + ownerName + "/\\" + nameC + "\n")

    if not(ownerName in ownerNames):
        ownerIdx += 1
        ownerNames[ownerName] = ownerIdx

    for comment in review['data']['comments']:
        name = Str(comment['reviewer']['name'])
        if ownerName != name:
            file1.write("CommentEdge" + "/\\" + ownerName + "/\\" + name + "\n")
        if not (name in commentRevNames):
            commentRevIdx += 1
            commentRevNames[name] = commentRevIdx


for name in uploaderNames:
    file2.write(name + "/\\" + str(uploaderNames[name]) + "\n")
for name in ownerNames:
    file3.write(name + "/\\" + str(ownerNames[name]) + "\n")
#commentRevNames represent the names of reviewers
for name in commentRevNames:
    file4.write(name + "/\\" + str(commentRevNames[name]) + "\n")
for name in approverNames:
    file5.write(name + "/\\" + str(approverNames[name]) + "\n")
for name in authorNames:
    file6.write(name + "/\\" + str(authorNames[name]) + "\n")
file1.close()
file2.close()
file3.close()
file4.close()
file5.close()
file6.close()
file8.close()
reviewData.close()
