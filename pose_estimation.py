# image 2 image의 Rt 계산
# camera coordinate to world coordinate calibration
# input : GeoTagImage 
# GeoTagImage에서 이미지 -> Rt, azimuth -> calibration
# 여기서 pose estimation 결과로 얻은 최종적인 추정 gps 값도 가져야 할듯

import cv2
import numpy as np

from geotag_image import GeoTagImage

class PoseEstimation:
    def __init__(self, retrieved, dataset):
        if not (isinstance(retrieved, GeoTagImage) and isinstance(dataset, GeoTagImage)):
            raise Exception('Argments(retrieved, dataset) are not GeoTagImage instance')
        self.retrieved_image = retrieved.get_image()
        self.dataset_image = dataset.get_image()
        self.dataset_azimuth = dataset.get_azimuth()

    def camera_to_world_calib(self):
        pass

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
        
        return rot, tran
    
    # todo
    # to_homogeneous()
    # recoveryPose에서 rotation이 어떤 축 순서 기준인지 확인해야 할듯. XYZ인지 뭔지