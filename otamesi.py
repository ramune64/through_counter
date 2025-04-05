import datetime
import csv
d_today = str(datetime.date.today())
t_now = str(datetime.datetime.now().time())
print(d_today+"-"+t_now)
date4 = str(d_today+"-"+t_now)
timea = int(date4.split(":")[0].split("-")[-1])
print(timea)
l= [[1,0],[3,4]]
with open('sample_writer_quote.csv', 'w',newline="") as f:
    writer = csv.writer(f)
    writer.writerows(l)

with open('2024-09-12-05-03-46.csv') as f:
    reader = csv.reader(f)
    rows = list(reader)
    print(rows)
    try:rows = list(reader)[-1]
    except IndexError:print("a-a")
# 0,1,2
# "a,b,c",x,y