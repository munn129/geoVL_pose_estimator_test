from geotag_image import GeoTagImage
from geo_error import GeoError
from image_retrieved import ImageRetrieved
from relative_pose import RelativePose

root_dir = 'patchnetvlad_workspace'
query_dir = '1114'
db_dir = '1024_1m'
query_gps = 'query_gps.txt'
db_gps = 'db_gps.txt'
retrieval_num = 2

# txt 파일을 읽어서, 이미지 리스트를 받아오는 함수 혹은 클래스 필요
# 혹은 GeoTagImage 클래스를 상속받아서,
# 텍스트 파일(image retrieval 결과)의 경로만 주면 알아서 하는 클래스

# 일단, 그 기능을 하는 함수
img_retrieval_result_dir = 'img_retrieval_result.txt'
# 일단 result에 있는 대로 읽은 후에, 나중에 중복을 제거하기 위해 _query~~
_query_name_list = []
dataset_name_list = []
with open(img_retrieval_result_dir, 'r') as file:
    for line in file:
        # 문자열 마지막에 '\n'으로 인해 indexing이 잘 안되는 문제 해결
        line = line.split('\n')[0]
        line = line.split(', ')
        # /patch.../.../~~.png -> patch.../.../~~.png
        _query_name_list.append(line[0][1:])
        # ~~.png\n -> ~~.png
        dataset_name_list.append(line[1][1:])

# query_name_list에서 중복되는 query_name을 지움
query_name_list = []
for i in _query_name_list:
    if i not in query_name_list:
        query_name_list.append(i)

# (query) list<GeoTagImage>
query_list = []
for i in query_name_list:
    query_list.append(GeoTagImage(str(i), query_gps))

# (dataset) list<GeoTagImage>
dataset_list = []
for i in dataset_name_list:
    dataset_list.append(GeoTagImage(str(i), db_gps))

retrieved_list = []
for i in range(len(query_list)):
    tmp_dataset_list = []
    for j in range(retrieval_num):
        tmp_dataset_list.append(dataset_list[i * 2 + j])

    retrieved_list.append(ImageRetrieved(query_list[i], tmp_dataset_list))

estimated_gps_list = []
for retrieved in retrieved_list:
    estimated_gps_list.append(RelativePose(retrieved).get_estimated_gps())

gt_gps_list = []
for query in query_list:
    gt_gps_list.append((query.get_latitude(), query.get_longitude()))

dataset_gps_list = []
for i in range(len(query_list)):
    gps = dataset_list[2 * i].get_latitude(), dataset_list[2 * i].get_longitude()
    dataset_gps_list.append(gps)

gps_error = GeoError(gt_gps_list, estimated_gps_list, 'gt', 'estimated')
gps_error.error_printer()

retrieved_error = GeoError(gt_gps_list, dataset_gps_list, 'gt', 'retrieved')
retrieved_error.error_printer()