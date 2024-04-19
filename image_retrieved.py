'''
image retrieval 결과를 저장하는 class
input
query: 쿼리 이미지(GeoTagImage instance)
retrieved_list: image retrieval 결과로 추천된 이미지들(list<GeoTagImage>)
'''

from geotag_image import GeoTagImage

class ImageRetrieved:
    def __init__(self, query: GeoTagImage, retrieved_list: list):
        if not(isinstance(query, GeoTagImage) and isinstance(retrieved_list[0], GeoTagImage)):
            raise Exception("All arguments must be GeoTagImage instance")
        
        self.query = query
        self.retrieved_list = retrieved_list

    def get_query(self) -> GeoTagImage:
        return self.query
    
    def get_retrieved_images(self) -> list:
        return self.retrieved_list