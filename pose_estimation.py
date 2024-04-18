# 카메라 좌표계와 gps 좌표계 사이의 캘리브레이션
# 두 이미지 사이의 R|t
# 값을 저장하는 클래스가 아님. 값을 계산하는 클래스임

# camera_to_world_calibration() -> 3*3 rotation matrix
# rt_calulator() -> 4*4 homogeneous matrix
# to_homogeneous() -> 4*4 homogeneous matrix
# 캘리브레이션 행렬도 4*4로 만들어서 나중에 캘리브레이션 할 수 있게 해야할 듯
# calibration matrix, rt, scale, gps 값을 입력으로 받아서
# estimation 하는 함수를 만들어야 할듯

import numpy as np
import cv2
from math import cos, sin, pi, sqrt

class PoseEstimation:
    def __init__(self):
        pass

    def to_homogeneous(self):
        pass

    def camera_to_world_calibration(self, azimuth):
        '''
        input
        azimuth: degree(float)
        ouput
        calibration_matrix(4*4 honogeneous np.array)
        '''
        # azimuth source: novatel inspva azimuth, CW(left-handed)
        # azimuth -> retrieved image(dataset)
        roll = 0
        pitch = 0
        # deg to rad
        yaw = pi / 180 * azimuth
        # translation vector
        translation_vector = [0, 0, 0, 1]
        # calibration matrix(homogeneous, 4*4)
        calibration_matrix = np.eye(4)
        # camera: XYZ -> ZX(-Y)
        mat = np.array([0,1,0,
                        0,0,-1,
                        1,0,0]).reshape(3,3)
        R_x = np.array([1,0,0,
                        0,cos(roll),-sin(roll),
                        0,sin(roll),cos(roll)]).reshape(3,3)
        R_y = np.array([cos(pitch),0,sin(pitch),
                        0,1,0,
                        -sin(pitch),0,cos(pitch)]).reshape(3,3)
        R_z = np.array([cos(yaw),-sin(yaw),0,
                        sin(yaw),cos(yaw),0,
                        0,0,1]).reshape(3,3)
        
        # to homogeneous
        calibration_matrix[:3,:3] = mat @ R_x @ R_y @ R_z
        calibration_matrix[:,3] = translation_vector

        return calibration_matrix

    def rt_calculator(self, retrieved_image, dataset_image):
        '''
        input
        retrieved_image: np.array
        dataset_image: np.array
        output
        rt_matrix: 4*4 homogeneous np.array
        '''
        sift = cv2.SIFT_create()

        query_kp, query_des = sift.detectAndCompute(retrieved_image, None)
        train_kp, train_des = sift.detectAndCompute(dataset_image, None)

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
        
        rt_matrix = np.eye(4)

        rt_matrix[:3, :3] = rot
        rt_matrix[:3, 3] = tran
        rt_matrix[3,3] = 1

        return rt_matrix
    
    def gps_estimation(self, calibration_matrix, rt_matrix, latitude, longitude, scale = 1):
        '''
        input
        calibration_matrix: 4*4 homogeneous np.array
        rt_matix: 4*4 homogeneous np.array
        scale: int
        latitude: float
        longiture: float
        ouput
        gps: tuple(latitude, longitude)
        '''
        H = calibration_matrix @ rt_matrix
        return (scale * H[0,3] + latitude, scale * H[1,3] + longitude)

    def gt_scale_calculator(self, query_latitude, query_longitude, train_lattitude, train_longitude):
        '''
        input
        all float
        output
        scale: float
        '''
        return sqrt((query_latitude - train_lattitude)**2 + (query_longitude - train_longitude)**2)