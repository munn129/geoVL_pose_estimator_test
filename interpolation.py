from geotag_image import GeoTagImage

root_dir = 'patchnetvlad_workspace'
query_dir = '1114'
db_dir = '1024_1m'
query_gps = 'query_gps.txt'
db_gps = 'db_gps.txt'

img = GeoTagImage(f'{root_dir}/{query_dir}/000002.png', 'query_gps.txt')

print('a')