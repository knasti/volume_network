import requests, ogr, json, geojson, csv
from shapely.geometry import shape
from database import Database, CursorFromConnectionFromPool

Database.initialise(user='postgres', password='ottrupbakker1', host='localhost', database='sogne')


geojson_sogn = []
sogne_codes = []
wkt_sogn = []
kbh_kom_sogn_kode = []
fre_kom_sogn_kode = []

# Sogne codes for Copenhagen municipality
for i in range(91):
    sogne_codes.append(7000 + i)

sogne_codes.append(9133)
sogne_codes.append(9161)
sogne_codes.append(9164)
sogne_codes.append(9165)
sogne_codes.append(9169)
sogne_codes.append(9174)
sogne_codes.append(9175)
sogne_codes.append(9182)
sogne_codes.append(9185)
sogne_codes.append(9190)

# Sogne Codes for Frederiksberg municiplaity
sogne_codes.append(7101)
sogne_codes.append(7102)
sogne_codes.append(7103)
sogne_codes.append(7104)
sogne_codes.append(7105)
sogne_codes.append(7106)
sogne_codes.append(7107)
sogne_codes.append(7108)
sogne_codes.append(7109)
sogne_codes.append(9128)
sogne_codes.append(9181)

print(sogne_codes)


for sogne_code in sogne_codes:
    temp_string = requests.get(
        'https://dawa.aws.dk/sogne/{}?format=geojson'.format(sogne_code)
    )

    if temp_string.status_code == 200:
        print(temp_string.json())
        geojson_sogn.append(temp_string.json())
        kbh_kom_sogn_kode.append('101' + str(sogne_code))
        fre_kom_sogn_kode.append('147' + str(sogne_code))

for i in range(len(geojson_sogn)):
    temp_dump = json.dumps(geojson_sogn[i]['geometry'])
    temp_dump = geojson.loads(temp_dump)
    wkt_sogn.append(shape(temp_dump))
    print(wkt_sogn[i])
    print(wkt_sogn[i].wkt)


with CursorFromConnectionFromPool() as cursor:
    cursor.execute("DROP TABLE IF EXISTS sogn")
    cursor.execute("CREATE TABLE sogn ( \
                        geom GEOMETRY, \
                        kbh_code INTEGER, \
                        fre_code INTEGER, \
                        volume INTEGER \
                        );")

with CursorFromConnectionFromPool() as cursor:
    cursor.execute("DROP TABLE IF EXISTS DST_Volume")
    cursor.execute("CREATE TABLE DST_Volume ( \
                        code BIGINT, \
                        volume BIGINT \
                        );")

for i in range(len(geojson_sogn)):
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute("INSERT INTO sogn (geom, kbh_code, fre_code) \
                        VALUES (ST_GeometryFromText(%s, 4326), %s, %s);", [wkt_sogn[i].wkt, int(kbh_kom_sogn_kode[i]), int(fre_kom_sogn_kode[i])])


with open(r'C:\Users\Niels\Desktop\sogn_volume_1.csv', newline='') as csvfile:
    sogn_volume_data = csv.reader(csvfile, delimiter=',')
    for row in sogn_volume_data:
        print(row)
        print(row[0])
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("INSERT INTO DST_Volume (code, volume) \
                                VALUES (%s, %s);", [row[0], row[1]])
        except:
            print('Not an integer')

with CursorFromConnectionFromPool() as cursor:
    cursor.execute("UPDATE sogn SET volume = dst_volume.volume \
                    FROM dst_volume WHERE dst_volume.code = sogn.kbh_code")
    cursor.execute("UPDATE sogn SET volume = dst_volume.volume \
                    FROM dst_volume WHERE dst_volume.code = sogn.fre_code")








'''
temp_string = requests.get('https://dawa.aws.dk/sogne/7002?format=geojson')
temp_string = temp_string.json()
print(temp_string)

temp_string = json.dumps(temp_string['geometry'])
print(temp_string)
temp_string = geojson.loads(temp_string)
print(temp_string)
temp_string = shape(temp_string)
print(temp_string)

print(temp_string.wkt)
'''


'''
for k in range(len(src_file)):
    # Creating a new table in postgres with the necessary columns
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute("DROP TABLE IF EXISTS {}".format(table_names[k]))
        cursor.execute("CREATE TABLE {} ( \
                            name VARCHAR(80), \
                            geom GEOMETRY, \
                            time_const FLOAT8, \
                            transport VARCHAR, \
                            line_number VARCHAR, \
                            connector INTEGER \
                            );".format(table_names[k]))
    # Opening the shapefile
    shapefile = ogr.Open(src_file[k])

    # Getting the layer from the shapefile
    layer = shapefile.GetLayer()
    print(table_names[k])

    # Looping through all features of the shapefile
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        name = repr(feature.GetField("name"))
        wkt = feature.GetGeometryRef().ExportToWkt()
        time_const = feature.GetField("time_const")
        connector = feature.GetField("connector")
        line_number = feature.GetField("l_number")
        # Storing the applicable values
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("INSERT INTO {} (name, geom, time_const, connector, line_number) \
                            VALUES (%s, ST_GeometryFromText(%s, 4326), %s, %s, %s);".format(table_names[k]),
                           [name, wkt, time_const, connector, line_number])
'''
