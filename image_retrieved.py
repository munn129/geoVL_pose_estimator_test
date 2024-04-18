# image retrieval 결과를 저장하는 class

from geotag_image import GeoTagImage

class ImageRetrieved:
    def __init__(self, query, retrieved_list):
        if not(isinstance(query, GeoTagImage) and isinstance(retrieved_list[0], GeoTagImage)):
            raise Exception("All arguments must be GeoTagImage instance")
        
        self.query = query
        self.retrieved_list = retrieved_list

    def get_query(self) -> GeoTagImage:
        return self.query
    
    def get_retrieved_images(self) -> list:
        return self.retrieved_list