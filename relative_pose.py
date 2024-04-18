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

from image_retrieved import ImageRetrieved
from pose_estimation import PoseEstimation

class RelativePose:
    def __init__(self, image_retrieved_instance):
        if not isinstance(image_retrieved_instance, ImageRetrieved):
            raise Exception('Input argumnet must be ImageRetrieved instance.')
        
        self.pose_estimation = PoseEstimation()

        self.query = image_retrieved_instance.get_query()
        self.camera_to_world_list = []
        self.rt_list = []
        self.gt_scale_list = []
        self.retrieved_gps_list = []
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