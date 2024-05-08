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
from ransac_filter import RANSACFilter

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

    img_retrieval_result_dir = 'NetVLAD_predictions_1m.txt'
    _query_name_list = []
    dataset_name_list = []
    with open(img_retrieval_result_dir, 'r') as file:
        for line in file:
            if line[0] == '#': continue
            line = line.split('\n')[0]
            line = line.split(', ')
            _query_name_list.append(line[0][1:])
            dataset_name_list.append(line[1][1:])

    query_name_list = []
    for i in _query_name_list:
        if i not in query_name_list:
            query_name_list.append(i)
        
    query_list = []
    for idx, val in enumerate(query_name_list):
        query_list.append(GeoTagImage(str(val), query_gps, idx, scale, '../../'))
    print('=====query list done=====')

    dataset_list = []
    for idx, val in tqdm(enumerate(dataset_name_list)):
        dataset_list.append(GeoTagImage(str(val), db_gps, idx, scale, '../../'))
    print('=====dataset list done=====')

    retrieved_list = []
    for i in range(len(query_list)):
        tmp_dataset_list = []
        for j in range(retrieval_num):
            tmp_dataset_list.append(dataset_list[i * retrieval_num + j])

        retrieved_list.append(RetrievedImage(query_list[i], tmp_dataset_list))

    print('=====retirieval result is saved=====')

    gt_gps_list = []
    for query in query_list:
        gt_gps_list.append((query.get_latitude(), query.get_longitude()))

    print('=====gt is saved=====')

    retrieval_result_list = []
    for i in tqdm(range(len(query_list)), desc = 'retrieval'):
        gps = dataset_list[retrieval_num * i].get_latitude(), dataset_list[retrieval_num * i].get_longitude()
        retrieval_result_list.append(gps)

    retrieved_error = GeoError(gt_gps_list, retrieval_result_list, 'gt', 'retrieval', True)
    retrieved_error.error_printer()


    markov_model = MarkovModel(retrieved_list)
    markov_gps_list = [i.get_gps() for i in markov_model.get_kf_geotag()]

    markov_error = GeoError(gt_gps_list, markov_gps_list, 'gt', 'kf', True)
    markov_error.error_printer()

    # gt_filter = MarkovModel(retrieved_list)
    # gt_result_list = [i.get_gps() for i in gt_filter.get_gt_filter()]
    
    # gt_filter_err = GeoError(gt_gps_list, gt_result_list, 'gt', 'gt_filter', True)
    # gt_filter_err.error_printer()

    ransac = RANSACFilter(retrieved_list)
    ransac_result = [i.get_gps() for i in ransac.get_ransac_filter()]
    ransac_err = GeoError(gt_gps_list, ransac_result, 'gt', 'ransac', True)
    ransac_err.error_printer()

    linear_err = GeoError(gt_gps_list, ransac.get_linear_interpolation(), 'gt', 'linear', True)
    linear_err.error_printer()
    

if __name__ == '__main__':
    main()
