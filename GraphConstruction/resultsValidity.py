from reproValidity import *

Y = 3600 * 24 * 30 * 12

timeInt = [3600, 3600 * 24, 3600 * 24 * 5, 3600 * 24 * 30, Y, Y * 2, Y * 5, Y * 10, Y * 20]


for delta_t in timeInt:
    initData()
    getValues(delta_t)
