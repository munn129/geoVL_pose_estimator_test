'''
성능이 좋지 못한 pose estimation by triangulation의 기능을
눈물을 머금고 분리...
사실 이 방법의 다양한 문제점들이 있음. 방향이나 기타 등등..
근데 이걸 해결하더라도, 큰 이점은 없을 것 같음...
'''

from retrieved_image import RetrievedImage
from triangulation import Triangulation
from pose_estimation import PoseEstimation

class TriangulationPose:
    def __init__(self, retrieved_image_instance: RetrievedImage) -> None:
        self.retrieved_list = retrieved_image_instance.get_retrieved_image_list()[:2]
        self.query = retrieved_image_instance.get_query()
        self.rt_list = []
        self.retrieved_gps_list = []
        self.triangulation = Triangulation()
        self.pose_estimation = PoseEstimation()
        
        for retrieved in self.retrieved_list:
            image_name = f'query: {self.query.get_image_path()}, retrieved: {retrieved.get_image_path()}'
            self.rt_list.append(self.pose_estimation.rt_calculator(self.query.get_image(),
                                                                   retrieved.get_image(),
                                                                   image_name))
            retrieved_latitude = retrieved.get_latitude()
            retrieved_longitude = retrieved.get_longitude()
            self.retrieved_gps_list.append((retrieved_latitude, retrieved_longitude))

        
        if not self.rt_list: raise Exception('make rt_list is failed')

        self.distance_between_retrieved_images = self.triangulation.scale_calculator(self.retrieved_list[0].get_latitude(),
                                                                                   self.retrieved_list[0].get_longitude(),
                                                                                   self.retrieved_list[1].get_latitude(),
                                                                                   self.retrieved_list[1].get_longitude())
        
        self.estimated_latitude = 0
        self.estimated_longitude = 0

    def triangle_estimate(self) -> None:
        # 쿼리 이미지가 촬영된 장소를 O = (0,0) 첫 번째 retrieved image의 촬영 장소를 A, 두번째를 B라 했을 때
        # alpha -> AOB, beta -> OAB, gamma -> OBA

        if len(self.rt_list) != 2: raise Exception('length of rt_list must be 2 for this fuction')

        vec_1 = self.triangulation.homogeneous_to_2d_vector(self.rt_list[0])
        vec_2 = self.triangulation.homogeneous_to_2d_vector(self.rt_list[1])
        alpha = self.triangulation.compute_angle_between_vectors(vec_1, vec_2)

        vec_3 = vec_1 - vec_2
        beta = self.triangulation.compute_angle_between_vectors(vec_1, vec_3)

        gamma = self.triangulation.triangle_angle(alpha, beta)

        x, y = self.triangulation.triangle_gps_estimate(alpha,
                                                          beta,
                                                          gamma,
                                                          self.distance_between_retrieved_images)
        
        estimated_latitude = self.retrieved_gps_list[0][0] + x
        estimated_longitude = self.retrieved_gps_list[0][1] + y

        # print(f'alpha: {alpha * 180 / 3.141592}, beta: {beta* 180 / 3.141592}, gamma: {gamma* 180 / 3.141592}')

        self.estimated_latitude = estimated_latitude
        self.estimated_longitude = estimated_longitude

    def get_triangulated_gps(self) -> tuple:
        self.triangle_estimate()
        return self.estimated_latitude, self.estimated_longitude