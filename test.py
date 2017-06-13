import csv

with open(r'C:\Users\Niels\Desktop\sogn_volume_1.csv', newline='') as csvfile:
    sogn_volume_data = csv.reader(csvfile, delimiter=',')
    for row in sogn_volume_data:
        print(row)