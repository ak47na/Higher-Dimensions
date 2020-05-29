import subprocess

file1 = open("D:\\Ak_work2019-2020\\hopee\\jarNames.txt", "r")
file2 = open("D:\\Ak_work2019-2020\\hopee\\extractedJars.txt", "w")

while True:
    crtL = file1.readline()
    if not crtL:
        break
    line = crtL.replace('/', '\\')
    cmd = 'jar tvf D:\\Ak_work2019-2020\\eclipseRepo\\' + line
    Lst = line.split('\\')
    Lst.pop()
    ans = subprocess.Popen(['jar', 'tvf', 'D:\\Ak_work2019-2020\\eclipseRepo\\' + line.replace('\n', '')],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    stdout, stderr = ans.communicate()
    files = stdout.decode("utf-8").split('\n')
    for file in files:
        fileName = file.split(' ')[-1].replace('\r', '')
        if fileName.replace('\n', '') == '':
            continue
        file2.write(fileName.replace('\n', ''))
        file2.write(' : ')
        file2.write(line)
file2.close()
file1.close()
