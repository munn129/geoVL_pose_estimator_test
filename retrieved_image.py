'''
image retrieval 결과를 저장하는 class
input
query: 쿼리 이미지(GeoTagImage instance)
retrieved_list: image retrieval 결과로 추천된 이미지들(list<GeoTagImage>)
'''

from geotag_image import GeoTagImage

class RetrievedImage:
    def __init__(self, query: GeoTagImage, retrieved_list: list):
        if not(isinstance(query, GeoTagImage) and isinstance(retrieved_list[0], GeoTagImage)):
            raise Exception("All arguments must be GeoTagImage instance")
        
        self.query = query
        self.retrieved_list = retrieved_list[:]

    def get_query(self) -> GeoTagImage:
        return self.query
    
    def get_retrieved_image_list(self) -> list:
        return self.retrieved_list
    
    def gps_to_meter(self, gps_1: tuple, gps_2: tuple) -> float:
            '''
            input
            - gps_1: tuple(latitude, longitude)
            - gps_2: tuple(latitude, longitude)
            output
            - distance of between gps_1 and gps_2 [m]
            '''

            from math import pi, sin, cos, atan2, sqrt

            lat1, lon1 = gps_1
            lat2, lon2 = gps_2

            # 지구의 넓이 반지름
            R = 6371.0072 # radius of the earth in KM
            lat_to_deg = lat2 * pi/180 - lat1 * pi/180
            long_to_deg = lon2 * pi/180 - lon1 * pi/180

            a = sin(lat_to_deg/2)**2 + cos(lat1 * pi/180) * cos(lat2 * pi/180) * sin(long_to_deg/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            d = R * c

            return d * 1000 #meter

    def eval(self) -> list:
        tmp = []
        for i in self.retrieved_list:
             e = self.gps_to_meter((self.query.get_latitude(),self.query.get_longitude()),
                                   (i.get_latitude(),i.get_longitude()))
             tmp.append(round(e, 3))
             
        return tmp