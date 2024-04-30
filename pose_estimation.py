'''
두 개의 이미지 사이의 rt, scale, calibration을 수행하는 클래스
"저장하는 데이터는 없다"
'''

import os

import numpy as np
import cv2
from math import cos, sin, pi, sqrt, asin

from camera_params import K, distortion_coefficients

class PoseEstimation:
    def __init__(self):
        pass

    def camera_to_world_calibration(self, azimuth: float):
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

    def rt_calculator(self, query_image, retrieved_image, scale, image_name = ''):
        '''
        input
        query_image: np.array
        retrieved_image: np.array
        output
        rt_matrix: 4*4 homogeneous np.array
        '''
        sift = cv2.SIFT_create()

        query_kp, query_des = sift.detectAndCompute(query_image, None)
        train_kp, train_des = sift.detectAndCompute(retrieved_image, None)

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


        rt_matrix = np.eye(4)

        if scale != 1:
            K[0,0] = K[0,0]/scale
            K[1,1] = K[1,1]/scale

        # Essential matrix가 제대로 나오지 않는 경우 발생
        # 3*3 사이즈가 아니거나, 혹은 None이 되버리는 경우, 혹은 확인되지 않은 오류 발생
        try:
            E, mask = cv2.findEssentialMat(query_points, train_points, K)
            retval, rot, tran, mask = cv2.recoverPose(E, query_points, train_points, K)
        except:
            print(f'find Essential matrix is failed at {image_name}')
            return rt_matrix

        rt_matrix[:3, :3] = rot
        rt_matrix[:3, 3] = tran.T

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

    def scale_calculator(self, query_latitude, query_longitude, train_lattitude, train_longitude):
        '''
        input
        all float
        output
        scale: float
        '''
        return sqrt((query_latitude - train_lattitude)**2 + (query_longitude - train_longitude)**2)

# for test(debug)
def main():
    root_dir = '../../patchnetvlad_workspace/data'
    query_dir = '0404_full'
    query_img = '000005.png'
    db_dir = '1024_1m'
    db_img = '002305.png'
    scale = 1

    img1_dir = os.path.join(root_dir, query_dir, query_img)
    img2_dir = os.path.join(root_dir, db_dir, db_img)

    img1 = cv2.imread(img1_dir)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    h, w = img1.shape[:2]
    print(f'h: {h}, w: {w}')
    img1_resized = cv2.resize(img1, (int(w/scale), int(h/scale)))

    img2 = cv2.imread(img2_dir)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img2_resized = cv2.resize(img2, (int(w/scale), int(h/scale)))

    pose_estimation = PoseEstimation()

    # rt_mat = pose_estimation.rt_calculator(img1_resized, img2_resized)
    rt_mat = rt_calculator(img1_resized, img2_resized, scale)


    print(rt_mat)

def rt_calculator(query_image, retrieved_image, scale, image_name = ''):
        '''
        input
        query_image: np.array
        retrieved_image: np.array
        output
        rt_matrix: 4*4 homogeneous np.array
        '''
        sift = cv2.SIFT_create()

        query_kp, query_des = sift.detectAndCompute(query_image, None)
        train_kp, train_des = sift.detectAndCompute(retrieved_image, None)

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


        rt_matrix = np.eye(4)

        if scale != 1:
            K[0,0] = K[0,0]/scale
            K[1,1] = K[1,1]/scale

        d = distortion_coefficients

        # E, mask = cv2.findEssentialMat(query_points,train_points, K)
        # retval, rot, tran, mask = cv2.recoverPose(E,query_points,train_points, K)

        E, mask = cv2.findEssentialMat(query_points,train_points)
        retval, rot, tran, mask = cv2.recoverPose(E,query_points,train_points)


        rt_matrix[:3, :3] = rot
        rt_matrix[:3, 3] = tran.T

        return rt_matrix

if __name__ == '__main__':
    main()