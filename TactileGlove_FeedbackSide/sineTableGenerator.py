import math

TABLE_SIZE = 256  # size of the sine table
sineTable = bytearray(TABLE_SIZE)  # declare the sine table as a byte array

# generate the sine table
for i in range(TABLE_SIZE):
    radians = (i * 2 * math.pi) / TABLE_SIZE
    sineTable[i] = round(127.0 + 127.0 * math.sin(radians - math.pi/2.0))

# print the sine table
for i in range(TABLE_SIZE):
    print(sineTable[i], end=', ')