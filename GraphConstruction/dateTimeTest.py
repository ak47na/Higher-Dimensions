from datetime import timedelta
from dateutil.parser import parse
import tzInfo

# this is sample example
tzInfo = tzInfo.getTZInfo()
date = 'Sun, 2 Jun 1996 16:43:00 -0700 (PDT)'
x = parse(date, tzinfos=tzInfo)
y = parse("Sun, 2 Jun 1996 16:43:00 UTC", tzinfos=tzInfo)
print(type(x), type(y))
print(x.timestamp() - y.timestamp())
print(x.timestamp(), y.timestamp())
print(x.tzinfo, y.tzinfo)