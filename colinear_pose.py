from retrieved_image import RetrievedImage
from colinear import Colinear

# interpolation이라고 하면,
# retrieved image의 경향이 어떻게 되는지 보여주어야 할 듯
class ColinearPose:
    def __init__(self, retrieved_image_instance: RetrievedImage) -> None:
        self.retrieved_image_instance = retrieved_image_instance
        self.query = retrieved_image_instance.get_query()
        self.retrieved_list = retrieved_image_instance.get_retrieved_image_list()
                
        self.inlier_mask = Colinear().filtering(self.retrieved_list)
        
        self.is_colinear = Colinear().colinear_detection()

        self.estimated_gps = Colinear().gaussian_ml(self.inlier_mask, self.retrieved_list)

    def get_estimated_gps(self):
        return self.estimated_gps