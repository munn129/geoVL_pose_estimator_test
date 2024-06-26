import random

from tqdm import tqdm

from geotag_image import GeoTagImage
from geo_error import GeoError
from retrieved_image import RetrievedImage
from relative_pose import RelativePose
from triangulation_pose import TriangulationPose
from colinear_pose import ColinearPose

from retrieval_distribution import RetrievalDistribution
from error_plot import ErrorPlot
from markov_model import MarkovModel

# 더 큰 간격에서 삼각측량
# 넷블라드를 프리징하고 트랜스포머?로 파인튜닝(우리 데이터셋으로 재학습)
# Zhou 방법에서 사용한 데이터 셋에서 평가하는 것도 방법임

def main():
    root_dir = '../../patchnetvlad_workspace/data'
    query_dir = '1024_1m'
    db_dir = '0404_full'
    query_gps = '0404_full_gps.txt'
    db_gps = '1024_1m_gps.txt'
    retrieval_num = 10
    scale = 5
    is_subset = False
    is_sequence_subset = 0
    if is_subset and is_sequence_subset: raise Exception('only one condition must be True')
    subset_num = 100


    # 일단, 그 기능을 하는 함수
    img_retrieval_result_dir = 'PatchNetVLAD_predictions_1m.txt'
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

    if is_sequence_subset:
        q_list = []
        d_list = []
        
        for i in range(subset_num):
            q_list.append(query_name_list[i])
            for j in range(retrieval_num):
                d_list.append(dataset_name_list[i*retrieval_num + j])

        query_name_list = q_list[:]
        dataset_name_list = d_list[:]
        
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
    # image retrieval 성능 평가
    retrieval_result_list = []
    for i in tqdm(range(len(query_list)), desc = 'retrieval'):
        gps = dataset_list[retrieval_num * i].get_latitude(), dataset_list[retrieval_num * i].get_longitude()
        retrieval_result_list.append(gps)

    retrieved_error = GeoError(gt_gps_list, retrieval_result_list, 'gt', 'retrieval')
    # retrieved_error.error_printer()

    # for i in retrieved_list:
    #     t = i.eval()
    #     if t[0] > 10:
    #         print(t)
    #         print(i.get_query().get_image_path())
    #         print(i.get_retrieved_image_list()[0].get_image_path())
    #         print('=================================')

    #markov

    # markov_model = MarkovModel(retrieved_list)
    # markov_gps_list = [i.get_gps() for i in markov_model.get_kf_geotag()]
    # markov_gps_list = [i.get_gps() for i in markov_model.get_filtered_geotag()]

    # for i in markov_model.get_filtered_geotag():
    #     print(i.get_image_path())

    # markov_error = GeoError(gt_gps_list, markov_gps_list, 'gt', 'markov')
    # markov_error.error_printer()
    
    # retrieved_error.error_printer()

    # retrieval 결과의 유형을 보기 위함
    distribution_list = []
    top = 3
    for i in retrieved_list:
        distribution_list.append(RetrievalDistribution(i, top))
    
    plot_instance = ErrorPlot(distribution_list, False)
    plot_instance.plot()

    # RelativePose 클래스에서 추정된 위치(gps)를 가져옴
    # RelativePose에서 연산하는 것 처럼 보이지만,
    # 실제로는 PoseEstimation 클래스에서 연산이 이뤄지고 있음
    # RelativePose는 관계된 값만 저장함
    # direct_result_list = []
    # idx = 0
    # for retrieved in tqdm(retrieved_list, desc = 'direct'):
    #     idx += 1
    #     direct_result_list.append(RelativePose(retrieved).get_direct_gps())

    # direct_error = GeoError(gt_gps_list, direct_result_list, 'gt', 'direct')
    # direct_error.error_printer()

    # # gps triangulation
    # triangulation_result_list = []
    # for retrieved in retrieved_list:
    #     triangulation_result_list.append(TriangulationPose(retrieved).get_triangulated_gps())

    # triangulation_error = GeoError(gt_gps_list, triangulation_result_list, 'gt', 'triangulation', True)
    # triangulation_error.error_printer()

    # # colinear
    # colinear_result_list = []
    # for retrieved in retrieved_list:
    #     colinear_result_list.append(ColinearPose(retrieved).get_estimated_gps())

    # colinear_error = GeoError(gt_gps_list, colinear_result_list, 'gt', 'colinear')
    # colinear_error.error_printer()

if __name__ == '__main__':
    main()
