# image 2 image의 Rt 계산
# camera coordinate to world coordinate calibration
# input : GeoTagImage 
# GeoTagImage에서 이미지 -> Rt, azimuth -> calibration
# 여기서 pose estimation 결과로 얻은 최종적인 추정 gps 값도 가져야 할듯

# 이 클래스에서 쿼리 이미지를 기준으로 retrieved image"들"의 정보를 같이 갖고 있는게 맞을까?
# 그렇다면, 어떻게 해야할까...
# 정보를 갖고 있는건 아닌듯, 데이터와 기능을 분리시켜야 함. -> iamge retrieved class
# 그리고 이 클래스에서는 ImageRetrieved 클래스 입력을 받아야 함

# 이 클래스에서는 image retrieved instance를 받고, 쿼리 이미지와 비교했을 때
# R|t 정보와 estimation된 값을 저장하는 편이 옳을 듯.
# R|t를 계산하는건 다른 클래스ㄱㄱ 그럼 얘 이름을 뭘로하지...

import cv2
import numpy as np
from math import cos, sin, pi

from geotag_image import GeoTagImage
from image_retrieved import ImageRetrieved
from pose_estimation import PoseEstimation

class RelativePose:
    def __init__(self, image_retrieved_instance):
        if not isinstance(image_retrieved_instance, ImageRetrieved):
            raise Exception('Input argumnet must be ImageRetrieved instance.')
        
        self.pose_estimation = PoseEstimation()

        # 여기서는 rt 값만 저장하면 되니까. 이미지를 저장하고 있을 이유가 없음
        self.query_geotagimage = image_retrieved_instance.get_query()
        # dataset_geotagimages -> list
        self.dataset_geotagimages = image_retrieved_instance.get_retrieved_images()
        self.query_latitude = self.query_geotagimage.get_latitude()
        self.query_longitude = self.query_geotagimage.get_longitude()
        
        
    def get_translation(self):
        self.camera_to_world_calib()
        self.rt_calculator()

        return self.mat @ self.translation.T