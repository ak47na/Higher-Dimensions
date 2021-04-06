from datetime import timedelta
import warnings
from dateutil import tz
from dateutil.parser import parse
import tzInfo

warnings.filterwarnings("error")

tzInfo = tzInfo.getTZInfo()
local_zone = tz.tzlocal()
dates = []
dates.append('Mon, 28 Feb 1995 04:49:44 UTC')

tstpExp = 793946984.0
print(tstpExp)
# dates.append('Sat, 6 Apr 1996 23:36:11 +0200 (MET)')
# dates.append('Sat, 6 Apr 1996 23:36:11 +0200 (UTC)')
# dates.append('Sat, 6 Apr 1996 23:36:11 +0100 (UTC)')
# dates.append('Sat, 6 Apr 1996 23:36:11 +0300 (UTC)')
# dates.append('Sat, 6 Apr 1996 23:36:11 UTC')
# dates.append('Sat, 6 Apr 1996 23:36:11 +0200 UTC')
dates.append('Sat, 6 Apr 1996 22:36:11 UTC')
# dates.append('Mon, 3 Apr 1995 23:06:27 EET')
# dates.append('Mon, 3 Apr 1995 21:06:27 UTC')
# dates.append('Mon, 3 Apr 1995 23:06:27')
# dates.append('Mon, 3 Apr 1995 23:06:27 +0200')
# dates.append('Mon, 3 Apr 1995 23:06:27 EET')
# dates.append('Mon, 3 Apr 1995 23:06:27')
# dates.append('1995-04-03 23:06:27+02:00')
# dates.append('1995-04-03 21:06:27+02:00')
# dates.append('1995-04-03 23:06:27')
# dates.append('Mon, 3 Apr 1995 23:06:27 UTC')
# dates.append('Mon, 3 Apr 1995 21:06:27 UTC')
for datee in dates:
    dte = parse(datee, tzinfos=tzInfo)
    print(datee, dte, dte.timestamp(), 'and utced', dte.astimezone(tz.gettz('UTC')))
    print('And converting to loca', dte.timestamp(), dte.astimezone(local_zone).timestamp())
    # if dte.tzinfo:
    #     sec = dte.utcoffset().total_seconds()
    #     #print('With utc offset', datee, dte, sec)
    # else:
    #     print('no tzinfo', datee, dte)