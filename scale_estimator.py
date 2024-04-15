import cv2
import numpy as np

from math import pi, sin, cos, atan2, sqrt

from geotag_image import GeoTagImage
from geo_error import GeoError

root_dir = 'patchnetvlad_workspace'
query_dir = '1114'
db_dir = '1024_1m'
query_gps = 'query_gps.txt'
db_gps = 'db_gps.txt'

# txt 파일을 읽어서, 이미지 리스트를 받아오는 함수 혹은 클래스 필요
# 혹은 GeoTagImage 클래스를 상속받아서,
# 텍스트 파일(image retrieval 결과)의 경로만 주면 알아서 하는 클래스

# 일단, 그 기능을 하는 함수
img_retrieval_result_dir = 'img_retrieval_result.txt'
_query_name_list = []
dataset_name_list = []
with open(img_retrieval_result_dir, 'r') as file:
    for line in file:
        line = line.split(', ')
        # /patch.../.../~~.png -> patch.../.../~~.png
        _query_name_list.append(line[0][1:])
        # ~~.png\n -> ~~.png
        dataset_name_list.append(line[1][1:])

# dataset_name_list 구조상 마지막 문자가 \n이걸로 되어 있어서, 계속 이미지를 못 읽음
# 와중에 마지막 열은 \n가 안붙어 있음 ㅋㅋ 

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

q1 = GeoTagImage(f'{root_dir}/{query_dir}/000002.png', query_gps)
q2 = GeoTagImage(f'{root_dir}/{query_dir}/001527.png', query_gps)
q3 = GeoTagImage(f'{root_dir}/{query_dir}/001923.png', query_gps)
q4 = GeoTagImage(f'{root_dir}/{query_dir}/002358.png', query_gps)
q5 = GeoTagImage(f'{root_dir}/{query_dir}/002865.png', query_gps)

d1 = GeoTagImage(f'{root_dir}/{db_dir}/000002.png', db_gps)
d2 = GeoTagImage(f'{root_dir}/{db_dir}/000008.png', db_gps)
d3 = GeoTagImage(f'{root_dir}/{db_dir}/001067.png', db_gps)
d4 = GeoTagImage(f'{root_dir}/{db_dir}/001068.png', db_gps)
d5 = GeoTagImage(f'{root_dir}/{db_dir}/001300.png', db_gps)
d6 = GeoTagImage(f'{root_dir}/{db_dir}/001301.png', db_gps)
d7 = GeoTagImage(f'{root_dir}/{db_dir}/001593.png', db_gps)
d8 = GeoTagImage(f'{root_dir}/{db_dir}/001592.png', db_gps)
d9 = GeoTagImage(f'{root_dir}/{db_dir}/001903.png', db_gps)
d10 = GeoTagImage(f'{root_dir}/{db_dir}/001902.png', db_gps)

# recovery pose
def iamge_rt_calculator(query, train) -> tuple:
    sift = cv2.SIFT_create()

    query_kp, query_des = sift.detectAndCompute(query, None)
    train_kp, train_des = sift.detectAndCompute(train, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(query_des, train_des, k = 2)

    query_points = []
    train_points = []

    for i, (m,n) in enumerate(matches):
        if m.distance < 0.8 * n.distance:
            # if m.distance is under 0.5, error occurs
            query_points.append(query_kp[m.queryIdx].pt)
            train_points.append(train_kp[m.trainIdx].pt)

    query_points = np.int32(query_points)
    train_points = np.int32(train_points)

    E, mask = cv2.findEssentialMat(query_points, train_points)
    retval, rot, tran, mask = cv2.recoverPose(E, query_points, train_points)
    
    return rot, tran

# Rt
q1_d1 = iamge_rt_calculator(q1.get_image(), d1.get_image())
q1_d2 = iamge_rt_calculator(q1.get_image(), d2.get_image())
q2_d3 = iamge_rt_calculator(q2.get_image(), d3.get_image())
q2_d4 = iamge_rt_calculator(q2.get_image(), d4.get_image())
q3_d5 = iamge_rt_calculator(q3.get_image(), d5.get_image())
q3_d6 = iamge_rt_calculator(q3.get_image(), d6.get_image())
q4_d7 = iamge_rt_calculator(q4.get_image(), d7.get_image())
q4_d8 = iamge_rt_calculator(q4.get_image(), d8.get_image())
q5_d9 = iamge_rt_calculator(q5.get_image(), d9.get_image())
q5_d10 = iamge_rt_calculator(q5.get_image(), d10.get_image())

# metric distance
def gps2meter(lat1, lon1, lat2, lon2) -> float:
    R = 6378.137 # radius of the earth in KM
    lat_to_deg = lat2 * pi/180 - lat1 * pi/180
    long_to_deg = lon2 * pi/180 - lon1 * pi/180

    a = sin(lat_to_deg/2)**2 + cos(lat1 * pi/180) * cos(lat2 * pi/180) * sin(long_to_deg/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c
    
    return d * 1000 # meter

# d1_d2_metric = gps2meter(d1.get_latitude(), d1.get_longitude(), d2.get_latitude(), d2.get_longitude())
# d3_d4_metric = gps2meter(d3.get_latitude(), d3.get_longitude(), d4.get_latitude(), d4.get_longitude())
# d5_d6_metric = gps2meter(d5.get_latitude(), d5.get_longitude(), d6.get_latitude(), d6.get_longitude())
# d7_d8_metric = gps2meter(d7.get_latitude(), d7.get_longitude(), d8.get_latitude(), d8.get_longitude())
# d9_d10_metric = gps2meter(d9.get_latitude(), d9.get_longitude(), d10.get_latitude(), d10.get_longitude())

d1_d2_rel_gps = sqrt((d1.get_latitude() - d2.get_latitude())**2 + (d1.get_longitude() - d2.get_longitude())**2)
d3_d4_rel_gps = sqrt((d3.get_latitude() - d4.get_latitude())**2 + (d3.get_longitude() - d4.get_longitude())**2)
d5_d6_rel_gps = sqrt((d5.get_latitude() - d6.get_latitude())**2 + (d5.get_longitude() - d6.get_longitude())**2)
d7_d8_rel_gps = sqrt((d7.get_latitude() - d8.get_latitude())**2 + (d7.get_longitude() - d8.get_longitude())**2)
d9_d10_rel_gps = sqrt((d9.get_latitude() - d10.get_latitude())**2 + (d9.get_longitude() - d10.get_longitude())**2)

d1_d2_rel_tvec = sqrt((q1_d1[1][2] - q1_d2[1][2])**2 + (q1_d1[1][1] - q1_d2[1][1])**2)
d3_d4_rel_tvec = sqrt((q2_d3[1][2] - q2_d4[1][2])**2 + (q2_d3[1][1] - q2_d4[1][1])**2)
d5_d6_rel_tvec = sqrt((q3_d5[1][2] - q3_d6[1][2])**2 + (q3_d5[1][1] - q3_d6[1][1])**2)
d7_d8_rel_tvec = sqrt((q4_d7[1][2] - q4_d8[1][2])**2 + (q4_d7[1][1] - q4_d8[1][1])**2)
d9_d10_rel_tvec = sqrt((q5_d9[1][2] - q5_d10[1][2])**2 + (q5_d9[1][1] - q5_d10[1][1])**2)

q1_d1_scale = d1_d2_rel_gps/d1_d2_rel_tvec
q2_d3_scale = d1_d2_rel_gps/d1_d2_rel_tvec
q3_d5_scale = d1_d2_rel_gps/d1_d2_rel_tvec
q4_d7_scale = d1_d2_rel_gps/d1_d2_rel_tvec
q5_d9_scale = d1_d2_rel_gps/d1_d2_rel_tvec

estiamte_q1 = d1.get_latitude() + q1_d1[1][2] * q1_d1_scale, d1.get_longitude() + q1_d1[1][1] * q1_d1_scale
estiamte_q2 = d3.get_latitude() + q2_d3[1][2] * q2_d3_scale, d3.get_longitude() + q2_d3[1][1] * q2_d3_scale
estiamte_q3 = d5.get_latitude() + q3_d5[1][2] * q3_d5_scale, d5.get_longitude() + q3_d5[1][1] * q3_d5_scale
estiamte_q4 = d7.get_latitude() + q4_d7[1][2] * q4_d7_scale, d7.get_longitude() + q4_d7[1][1] * q4_d7_scale
estiamte_q5 = d9.get_latitude() + q5_d9[1][2] * q5_d9_scale, d9.get_longitude() + q5_d9[1][1] * q5_d9_scale

error1 = gps2meter(q1.get_latitude(), q1.get_longitude(), estiamte_q1[0], estiamte_q1[1])
error2 = gps2meter(q2.get_latitude(), q2.get_longitude(), estiamte_q2[0], estiamte_q2[1])
error3 = gps2meter(q3.get_latitude(), q3.get_longitude(), estiamte_q3[0], estiamte_q3[1])
error4 = gps2meter(q4.get_latitude(), q4.get_longitude(), estiamte_q4[0], estiamte_q4[1])
error5 = gps2meter(q5.get_latitude(), q5.get_longitude(), estiamte_q5[0], estiamte_q5[1])

print('estimate error')
print(f'gps: {estiamte_q1}/ Error: {error1}')
print(f'gps: {estiamte_q2}/ Error: {error2}')
print(f'gps: {estiamte_q3}/ Error: {error3}')
print(f'gps: {estiamte_q4}/ Error: {error4}')
print(f'gps: {estiamte_q5}/ Error: {error5}')
print('=====================================')

error1 = gps2meter(q1.get_latitude(), q1.get_longitude(), d1.get_latitude(), d1.get_longitude())
error2 = gps2meter(q2.get_latitude(), q2.get_longitude(), d3.get_latitude(), d3.get_longitude())
error3 = gps2meter(q3.get_latitude(), q3.get_longitude(), d5.get_latitude(), d5.get_longitude())
error4 = gps2meter(q4.get_latitude(), q4.get_longitude(), d7.get_latitude(), d7.get_longitude())
error5 = gps2meter(q5.get_latitude(), q5.get_longitude(), d9.get_latitude(), d9.get_longitude())

print('retrieval error')
print(f'gps: {d1.get_latitude(), d1.get_longitude()}/ Error: {error1}')
print(f'gps: {d3.get_latitude(), d3.get_longitude()}/ Error: {error2}')
print(f'gps: {d5.get_latitude(), d5.get_longitude()}/ Error: {error3}')
print(f'gps: {d7.get_latitude(), d7.get_longitude()}/ Error: {error4}')
print(f'gps: {d9.get_latitude(), d9.get_longitude()}/ Error: {error5}')
print('=====================================')

# interpolation
estiamte_q1 = (d1.get_latitude() + d2.get_latitude())/2 , (d1.get_longitude() + d2.get_longitude())/2
estiamte_q2 = (d3.get_latitude() + d4.get_latitude())/2 , (d3.get_longitude() + d4.get_longitude())/2
estiamte_q3 = (d5.get_latitude() + d6.get_latitude())/2 , (d5.get_longitude() + d6.get_longitude())/2
estiamte_q4 = (d7.get_latitude() + d8.get_latitude())/2 , (d7.get_longitude() + d8.get_longitude())/2
estiamte_q5 = (d9.get_latitude() + d10.get_latitude())/2 , (d9.get_longitude() + d10.get_longitude())/2

error1 = gps2meter(q1.get_latitude(), q1.get_longitude(), estiamte_q1[0], estiamte_q1[1])
error2 = gps2meter(q2.get_latitude(), q2.get_longitude(), estiamte_q2[0], estiamte_q2[1])
error3 = gps2meter(q3.get_latitude(), q3.get_longitude(), estiamte_q3[0], estiamte_q3[1])
error4 = gps2meter(q4.get_latitude(), q4.get_longitude(), estiamte_q4[0], estiamte_q4[1])
error5 = gps2meter(q5.get_latitude(), q5.get_longitude(), estiamte_q5[0], estiamte_q5[1])

print('interpolation error')
print(f'gps: {estiamte_q1}/ Error: {error1}')
print(f'gps: {estiamte_q2}/ Error: {error2}')
print(f'gps: {estiamte_q3}/ Error: {error3}')
print(f'gps: {estiamte_q4}/ Error: {error4}')
print(f'gps: {estiamte_q5}/ Error: {error5}')
print('=====================================')