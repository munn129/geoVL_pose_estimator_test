from math import pi, sin, cos, sqrt, atan2

def gps_to_meter(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:

    # 지구의 넓이 반지름
    R = 6371.0072 # radius of the earth in KM
    lat_to_deg = lat2 * pi/180 - lat1 * pi/180
    long_to_deg = lon2 * pi/180 - lon1 * pi/180

    a = sin(lat_to_deg/2)**2 + cos(lat1 * pi/180) * cos(lat2 * pi/180) * sin(long_to_deg/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c

    return d * 1000 #meter

def result_writer(self,
                    query_name: str,
                    dataset_name: str,
                    translation_error: float,
                    rotation_error: float) -> None:
    
    pass