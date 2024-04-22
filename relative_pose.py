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
    
        # proposal
        # 이후 변수들은 제안하는 방법을 위한 변수들임
        self.distance_retrieved_images = 0
        retrieved_list = retrieved_image_instance.get_retrieved_image_list()
        if len(retrieved_list) == 2:
            self.distance_retrieved_images = self.pose_estimation.scale_calculator(retrieved_list[0].get_latitude(),
                                                                                   retrieved_list[0].get_longitude(),
                                                                                   retrieved_list[1].get_latitude(),
                                                                                   retrieved_list[1].get_longitude())
    
        # 쿼리 이미지가 촬영된 장소를 O = (0,0) 첫 번째 retrieved image의 촬영 장소를 A, 두번째를 B라 했을 때
        # alpha -> OAB
        # beta -> OBA
        # gamma -> AOB
        # self.alpha = 0
        # self.beta = 0
        # self.gamma = 0
        # self.estimated_gps = 0,0

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
            
        # retrieved top1 이미지의 결과 -> (latitude, longitude)
        return estimated_gps[0]
    
    def triangle_estimate(self):
        # 쿼리 이미지가 촬영된 장소를 O = (0,0) 첫 번째 retrieved image의 촬영 장소를 A, 두번째를 B라 했을 때
        # alpha -> OAB
        # beta -> OBA
        # gamma -> AOB

        if len(self.rt_list) != 2: raise Exception('length of rt_list must be 2 for this fuction')

        vec_1 = self.pose_estimation.homogeneous_to_2d_vector(self.rt_list[0])
        vec_2 = self.pose_estimation.homogeneous_to_2d_vector(self.rt_list[1])
        gamma = self.pose_estimation.compute_angle_between_vectors(vec_1, vec_2)

        vec_3 = [self.distance_retrieved_images, 0]
        alpha = self.pose_estimation.compute_angle_between_vectors(vec_1, vec_3)

        beta = self.pose_estimation.triangle_angle(alpha, gamma)

        x, y = self.pose_estimation.triangle_gps_estimate(alpha,
                                                          beta,
                                                          gamma,
                                                          self.distance_retrieved_images)
        
        estimated_latitude = self.retrieved_gps_list[0][0] + x
        estimated_longitude = self.retrieved_gps_list[0][1] + y

        return estimated_latitude, estimated_longitude