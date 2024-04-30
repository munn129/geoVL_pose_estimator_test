from math import pi, sin, cos, atan2, sqrt

import numpy as np

class Colinear:
    def __init__(self):
        pass

    # remove outlier
    def filtering(self, retrieved_image_list) -> list:

        list_len = len(retrieved_image_list)
        distance_list = np.zeros((list_len, list_len))

        for i in range(list_len):
            for j in range(i+1, list_len):
                i_gps = retrieved_image_list[i].get_latitude(), retrieved_image_list[i].get_longitude()
                j_gps = retrieved_image_list[j].get_latitude(), retrieved_image_list[j].get_longitude()
                distance_list[i, j] = self.gps_to_meter(i_gps, j_gps)
                distance_list[j, i] = distance_list[i, j]

        average = np.mean(distance_list)
        inlier_mask = np.where(distance_list < average/2, 1, 0)[0]

        return inlier_mask
    
    def gps_to_meter(self, gps_1: tuple, gps_2: tuple) -> float:
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

    # rt_cal
    def colinear_detection(self) -> bool:
        # colinear situation
        # 90 90 0, 0 0 180
        return True

    # avr
    def gaussian_ml(self, inlier_mask, retrieved_list) -> tuple:

        zero_cnt = 0
        for i in inlier_mask:
            if i: zero_cnt += 1

        _weights = [ 2**i for i in range(zero_cnt - 1)]
        _weights.append(100 - sum(_weights))
        weights = _weights[::-1]

        lat_sum = 0
        lon_sum = 0
        cnt = 0
        for inlier, retrieved in zip(inlier_mask, retrieved_list):
            if inlier:
                lat_sum += retrieved.get_latitude() * (weights[cnt]/100)
                lon_sum += retrieved.get_longitude() * (weights[cnt]/100)
                cnt += 1
        
        return lat_sum, lon_sum

def main():
    pass

if __name__ == '__main__':
    main()

