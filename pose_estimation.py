# image 2 image의 Rt 계산
# camera coordinate to world coordinate calibration
# input : GeoTagImage 
# GeoTagImage에서 이미지 -> Rt, azimuth -> calibration
# 여기서 pose estimation 결과로 얻은 최종적인 추정 gps 값도 가져야 할듯

# 이 클래스에서 쿼리 이미지를 기준으로 retrieved image"들"의 정보를 같이 갖고 있는게 맞을까?
# 그렇다면, 어떻게 해야할까...
# 정보를 갖고 있는건 아닌듯, 데이터와 기능을 분리시켜야 함. -> iamge retrieved class
# 그리고 이 클래스에서는 ImageRetrieved 클래스 입력을 받아야 함

import cv2
import numpy as np
from math import cos, sin, pi

from geotag_image import GeoTagImage
from image_retrieved import ImageRetrieved

class PoseEstimation:
    def __init__(self, retrieved, dataset):
        if not all(isinstance(obj, GeoTagImage) for obj in [retrieved, dataset]):
            raise Exception('Argments(retrieved, dataset) are not GeoTagImage instance')
        self.retrieved_image = retrieved.get_image()
        self.dataset_image = dataset.get_image()
        self.dataset_azimuth = dataset.get_azimuth()
        self.mat = np.zeros((3,3))
        self.translation = 0

    def __init(self, image_retrieved_instance):
        if not isinstance(image_retrieved_instance, ImageRetrieved):
            raise Exception('Input argumnet must be ImageRetrieved instance.')
        
        self.image_retrieved_instance = image_retrieved_instance
        self.query_geotagimage = image_retrieved_instance.get_query()
        self.dataset_geotagimages = image_retrieved_instance.get_retrieved_images()

    def camera_to_world_calib(self):
        # azimuth source: novatel inspva azimuth, CW(left-handed)
        roll = 0
        pitch = 0
        # deg to rad
        yaw = pi / 180 * self.dataset_azimuth
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
        
        self.mat =  mat @ R_x @ R_y @ R_z

    def rt_calculator(self):
        sift = cv2.SIFT_create()

        query_kp, query_des = sift.detectAndCompute(self.retrieved_image, None)
        train_kp, train_des = sift.detectAndCompute(self.dataset_image, None)

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
        
        self.translation = tran

    def get_translation(self):
        self.camera_to_world_calib()
        self.rt_calculator()

        return self.mat @ self.translation