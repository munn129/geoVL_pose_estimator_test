# ZHOU, Qunjie, et al. To learn or not to learn: Visual localization from essential matrices. In: 2020 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2020. p. 3319-3326.

from retrieved_image import RetrievedImage
from triangulation import Triangulation
from pose_estimation import PoseEstimation

class Z_Triangulation_pose:
    def __init__(self, retrieved_image_instance: RetrievedImage):
        self.retrieved_list = retrieved_image_instance.get_retrieved_image_list()[:2]
        self.query = retrieved_image_instance.get_query()
        self.rt_list = []
        self.retrieved_gps_list = []
        self.triangulation = Triangulation()
        self.pose_estimation = PoseEstimation()

class Z_Triangulation:
    def __init__(self):
        pass