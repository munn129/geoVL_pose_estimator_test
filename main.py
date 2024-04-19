from geotag_image import GeoTagImage
from geo_error import GeoError
from retrieved_image import RetrievedImage
from relative_pose import RelativePose

root_dir = 'patchnetvlad_workspace'
query_dir = '1114'
db_dir = '1024_1m'
query_gps = 'query_gps.txt'
db_gps = 'db_gps.txt'
retrieval_num = 2
scale = 10

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
    query_list.append(GeoTagImage(str(i), query_gps, scale))

# (dataset) list<GeoTagImage>
dataset_list = []
for i in dataset_name_list:
    dataset_list.append(GeoTagImage(str(i), db_gps, scale))

# 쿼리 이미지와 image retrieval 결과를 저장
# 쿼리 이미지 - [retrieved images, ...] 로 구성되어 있음
retrieved_list = []
for i in range(len(query_list)):
    tmp_dataset_list = []
    for j in range(retrieval_num):
        tmp_dataset_list.append(dataset_list[i * retrieval_num + j])

    retrieved_list.append(RetrievedImage(query_list[i], tmp_dataset_list))

# RelativePose 클래스에서 추정된 위치(gps)를 가져옴
# RelativePose에서 연산하는 것 처럼 보이지만,
# 실제로는 PoseEstimation 클래스에서 연산이 이뤄지고 있음
# RelativePose는 관계된 값만 저장함
estimated_gps_list = []
for retrieved in retrieved_list:
    estimated_gps_list.append(RelativePose(retrieved).get_estimated_gps())

# 쿼리 이미지가 촬영된 위치를 저장
gt_gps_list = []
for query in query_list:
    gt_gps_list.append((query.get_latitude(), query.get_longitude()))

# retrieved 이미지가 촬영된 위치를 저장
dataset_gps_list = []
for i in range(len(query_list)):
    gps = dataset_list[2 * i].get_latitude(), dataset_list[2 * i].get_longitude()
    dataset_gps_list.append(gps)

gps_error = GeoError(gt_gps_list, estimated_gps_list, 'gt', 'estimated')
gps_error.error_printer()

retrieved_error = GeoError(gt_gps_list, dataset_gps_list, 'gt', 'retrieved')
retrieved_error.error_printer()