# evaluation of retrieval result
# image retrieval 결과가 어떠한 경향을 띄는지 보기 위함

from math import pi, sin, cos, sqrt, atan2

from retrieved_image import RetrievedImage

class RetrievalDistribution:
    def __init__(self, retrieved_instance: RetrievedImage, use_num = 1) -> None:
        self.query = retrieved_instance.get_query()
        self.retrieved_list = retrieved_instance.get_retrieved_image_list()
        self.query_gps = self.query.get_latitude(), self.query.get_longitude()
        self.retrieved_gps_list = []
        for retrieved in self.retrieved_list:
            self.retrieved_gps_list.append((retrieved.get_latitude(), retrieved.get_longitude()))

        self.topological_error_list = []
        self.topological_latitude_error_list = []
        self.topological_longitude_error_list = []
        self.latitude_meter = []
        self.longitude_meter = []

        for i in range(use_num):
            latitude = self.query_gps[0] - self.retrieved_gps_list[i][0]
            longitude = self.query_gps[1] - self.retrieved_gps_list[i][1]
            self.topological_error_list.append((latitude, longitude))
            self.topological_latitude_error_list.append(latitude)
            self.topological_longitude_error_list.append(longitude)

    def get_topological_error_list(self):
        return self.topological_error_list
    
    def get_topological_latitude_list(self):
        return self.topological_latitude_error_list
    
    def get_topological_longitude_list(self):
        return self.topological_longitude_error_list
    
    def _gps_to_meter(self, gps_1: tuple, gps_2: tuple) -> float:
        '''
        input
        - gps_1: tuple(latitude, longitude)
        - gps_2: tuple(latitude, longitude)
        output
        - distance of between gps_1 and gps_2 [m]
        '''
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

    def get_latitude_meter(self):
        # something wrong
        for i in self.topological_latitude_error_list:
            self.latitude_meter.append(self._gps_to_meter((0,0), (i, 0)))

        return self.latitude_meter
    
    def get_longitude_meter(self):
        # something wrong
        for i in self.topological_longitude_error_list:
            self.longitude_meter.append(self._gps_to_meter((0,0), (i, 0)))

        return self.longitude_meter

def main():
    pass

if __name__ == '__main__': main()