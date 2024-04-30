import random

from tqdm import tqdm

from geotag_image import GeoTagImage
from geo_error import GeoError
from retrieved_image import RetrievedImage
from relative_pose import RelativePose
from triangulation_pose import TriangulationPose

import cv2


def main():
    root_dir = '../../patchnetvlad_workspace/data'
    query_dir = '1024_1m'
    db_dir = '0404_full'
    query_gps = '0404_full_gps.txt'
    db_gps = '1024_1m_gps.txt'
    retrieval_num = 10
    scale = 2
    is_subset = True
    subset_num = 50

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

    print(query_list[0].get_image_path())
    cv2.imshow('image', query_list[0].get_image())
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    main()