'''
ImageRetrieved instance에 있는 쿼리 이미지와 retrieved 이미지 사이의
rt, scale 등을 저장하는 클래스
아직 고쳐야 할 부분이 많다...
input
- retrieved_image_instance : RetrievedImage
- query: GeoTagImage, list<retrieved image: GeoTagImage>
'''

from retrieved_image import RetrievedImage
from pose_estimation import PoseEstimation

class RelativePose:
    def __init__(self, retrieved_image_instance: RetrievedImage):
        if not isinstance(retrieved_image_instance, RetrievedImage):
            raise Exception('Input argumnet must be RetrievedImage instance.')

        self.retrieved_gps_list = retrieved_image_instance        
        self.pose_estimation = PoseEstimation()

        self.query = retrieved_image_instance.get_query()
        self.camera_to_world_list = []
        self.rt_list = []
        self.gt_scale_list = []
        self.retrieved_gps_list = []
        # 가능하면 이 부분을 좀 분리하고 싶긴 함
        # 근데 또 내가 제안하는 방법에서 rt가 필요하기 때문에 init 함수에서 값을 처리하는게 맞는거 같기도...
        for retrieved in retrieved_image_instance.get_retrieved_image_list():
            retrieved_latitude = retrieved.get_latitude()
            retrieved_longitude = retrieved.get_longitude()
            self.camera_to_world_list.append(self.pose_estimation.camera_to_world_calibration(retrieved.get_azimuth()))
            self.rt_list.append(self.pose_estimation.rt_calculator(self.query.get_image(),
                                                                   retrieved.get_image()))
            self.gt_scale_list.append(self.pose_estimation.scale_calculator(self.query.get_latitude(),
                                                                            self.query.get_longitude(),
                                                                            retrieved_latitude,
                                                                            retrieved_longitude))
            self.retrieved_gps_list.append((retrieved_latitude, retrieved_longitude))

        if not self.camera_to_world_list or not self.rt_list or not self.gt_scale_list:
            raise Exception('some work is failed')
        
        if not len(self.camera_to_world_list) == len(self.rt_list):
            raise Exception('calibration list and rt list have different length')
    
        self.distance_retrieved_images = 0
        retrieved_list = retrieved_image_instance.get_retrieved_image_list()
        if len(retrieved_list) == 2:
            self.distance_retrieved_images = self.pose_estimation.scale_calculator(retrieved_list[0].get_latitude(),
                                                                                   retrieved_list[0].get_longitude(),
                                                                                   retrieved_list[1].get_latitude(),
                                                                                   retrieved_list[1].get_longitude())
    
    def direct_estimate(self):
        # 이 배열의 길이는 retrieval image의 수
        # 나의 경우 쿼리 이미지 한 장에 retrieved image 2장을 골랐기 때문에 길이는 2
        estimated_gps = []
        # for calib, rt, gps in zip(self.camera_to_world_list, self.rt_list, self.retrieved_gps_list):
        for i in range(len(self.retrieved_gps_list)):
            estimated_gps.append(self.pose_estimation.gps_estimation(self.camera_to_world_list[i],
                                                                          self.rt_list[i],
                                                                          self.retrieved_gps_list[i][0], # latitude
                                                                          self.retrieved_gps_list[i][1], # longitude
                                                                          self.gt_scale_list[i]))
            
        # retrieved top1 이미지의 결과
        return estimated_gps[0]
    
    def triangulation_estimate(self):
        pass