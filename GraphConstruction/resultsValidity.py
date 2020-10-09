import reproValidity
import mailID

# the number of seconds in a year
Y = 3600 * 24 * 365

timeInt = [3600, 3600 * 24, 3600 * 24 * 5, 3600 * 24 * 30, Y, Y * 2, Y * 5, Y * 10, Y * 20]
mailID.init()
for delta_t in timeInt:
    reproValidity.getValues(delta_t)
