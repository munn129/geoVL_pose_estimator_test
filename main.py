import random

from tqdm import tqdm

from geotag_image import GeoTagImage
from geo_error import GeoError
from retrieved_image import RetrievedImage
from relative_pose import RelativePose
from triangulation_pose import TriangulationPose

root_dir = '../../patchnetvlad_workspace/data'
query_dir = '1024_1m'
db_dir = '0404_full'
query_gps = '0404_full_gps.txt'
db_gps = '1024_1m_gps.txt'
retrieval_num = 10
scale = 2
is_subset = True
subset_num = 100

# 일단, 그 기능을 하는 함수
img_retrieval_result_dir = 'PatchNetVLAD_predictions.txt'
# 일단 result에 있는 대로 읽은 후에, 나중에 중복을 제거하기 위해 _query~~
_query_name_list = []
dataset_name_list = []
with open(img_retrieval_result_dir, 'r') as file:
    for line in file:
        if line[0] == '#': continue
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

if is_subset:
    subset_index = []
    for _ in range(0, subset_num):
        random_int = random.randint(0, len(query_name_list))
        if random_int not in subset_index:
            subset_index.append(random_int)

    q_list = []
    d_list = []
    for i in subset_index:
        q_list.append(query_name_list[i])
        for j in range(0, retrieval_num):
            d_list.append(dataset_name_list[i * retrieval_num + j])

    query_name_list = []
    query_name_list = q_list
    dataset_name_list = []
    dataset_name_list = d_list
    
# (query) list<GeoTagImage>
query_list = []
for idx, val in enumerate(query_name_list):
    query_list.append(GeoTagImage(str(val), query_gps, idx, scale, '../../'))
print('=====query list done=====')

# (dataset) list<GeoTagImage>
# 이 부분에서 시간이 너무 오래 걸림...
dataset_list = []
for idx, val in tqdm(enumerate(dataset_name_list)):
    dataset_list.append(GeoTagImage(str(val), db_gps, idx, scale, '../../'))
print('=====dataset list done=====')

# 쿼리 이미지와 image retrieval 결과를 저장
# 쿼리 이미지 - [retrieved images, ...] 로 구성되어 있음
retrieved_list = []
for i in range(len(query_list)):
    tmp_dataset_list = []
    for j in range(retrieval_num):
        tmp_dataset_list.append(dataset_list[i * retrieval_num + j])

    retrieved_list.append(RetrievedImage(query_list[i], tmp_dataset_list))

print('=====retirieval result is saved=====')

# 쿼리 이미지가 촬영된 위치를 저장
gt_gps_list = []
for query in query_list:
    gt_gps_list.append((query.get_latitude(), query.get_longitude()))

print('=====gt is saved=====')

# retrieved 이미지가 촬영된 위치를 저장
retrieval_result_list = []
for i in tqdm(range(len(query_list)), desc = 'retrieval'):
    gps = dataset_list[retrieval_num * i].get_latitude(), dataset_list[retrieval_num * i].get_longitude()
    retrieval_result_list.append(gps)

retrieved_error = GeoError(gt_gps_list, retrieval_result_list, 'gt', 'retrieval')
retrieved_error.error_printer()

# RelativePose 클래스에서 추정된 위치(gps)를 가져옴
# RelativePose에서 연산하는 것 처럼 보이지만,
# 실제로는 PoseEstimation 클래스에서 연산이 이뤄지고 있음
# RelativePose는 관계된 값만 저장함
estimated_gps_list = []
idx = 0
for retrieved in tqdm(retrieved_list, desc = 'direct'):
    idx += 1
    estimated_gps_list.append(RelativePose(retrieved).get_direct_gps())

gps_error = GeoError(gt_gps_list, estimated_gps_list, 'gt', 'direct')
gps_error.error_printer()

# gps triangulation
# 원래는 위 코드랑 합칠 수 있음
triangulation_result_list = []
for retrieved in retrieved_list:
    triangulation_result_list.append(TriangulationPose(retrieved).get_triangulated_gps())

triangulation_error = GeoError(gt_gps_list, triangulation_result_list, 'gt', 'triangulation')
triangulation_error.error_printer()