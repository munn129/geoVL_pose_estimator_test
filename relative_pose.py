'''
ImageRetrieved instance에 있는 쿼리 이미지와 retrieved 이미지 사이의
rt, scale 등을 저장하는 클래스
아직 고쳐야 할 부분이 많다...
'''

from image_retrieved import ImageRetrieved
from pose_estimation import PoseEstimation

class RelativePose:
    def __init__(self, image_retrieved_instance: ImageRetrieved):
        if not isinstance(image_retrieved_instance, ImageRetrieved):
            raise Exception('Input argumnet must be ImageRetrieved instance.')
        
        self.pose_estimation = PoseEstimation()

        self.query = image_retrieved_instance.get_query()
        self.camera_to_world_list = []
        self.rt_list = []
        self.gt_scale_list = []
        self.retrieved_gps_list = []
        # 가능하면 이 부분을 좀 분리하고 싶긴 함
        for retrieved in image_retrieved_instance.get_retrieved_images():
            retrieved_latitude = retrieved.get_latitude()
            retrieved_longitude = retrieved.get_longitude()
            self.camera_to_world_list.append(self.pose_estimation.camera_to_world_calibration(retrieved.get_azimuth()))
            self.rt_list.append(self.pose_estimation.rt_calculator(self.query.get_image(),
                                                                   retrieved.get_image()))
            self.gt_scale_list.append(self.pose_estimation.gt_scale_calculator(self.query.get_latitude(),
                                                                          self.query.get_longitude(),
                                                                          retrieved_latitude,
                                                                          retrieved_longitude))
            self.retrieved_gps_list.append((retrieved_latitude, retrieved_longitude))

        if not self.camera_to_world_list or not self.rt_list or not self.gt_scale_list:
            raise Exception('some work is failed')
        
        if not len(self.camera_to_world_list) == len(self.rt_list):
            raise Exception('calibration list and rt list have different length')
    
        self.estimated_gps = []
        # for calib, rt, gps in zip(self.camera_to_world_list, self.rt_list, self.retrieved_gps_list):
        for i in range(len(self.retrieved_gps_list)):
            self.estimated_gps.append(self.pose_estimation.gps_estimation(self.camera_to_world_list[i],
                                                                          self.rt_list[i],
                                                                          self.retrieved_gps_list[i][0],
                                                                          self.retrieved_gps_list[i][1],
                                                                          self.gt_scale_list[i]))

    def get_estimated_gps(self):
        return self.estimated_gps[0]