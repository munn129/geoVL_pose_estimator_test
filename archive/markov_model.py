# 일단은... 과거 retrieved 결과를 받아야 함. 어능정도까지?
# 그냥 직전 스텝만 받아서, 마르코프 체인이라 하자

# 이게 이 클래스에서 직전 단계만 받아서 처리하면 좋겠지만,
# 필터링한 결과를 계속 업데이트하려면, 메인 파일에서 바꿔야할 것 같으니
# 일단... 여기서 전부 처리하는 걸로

from math import pi, sin, cos, sqrt, atan2
from collections import namedtuple

import numpy as np

from retrieved_image import RetrievedImage
from geotag_image import GeoTagImage

class MarkovModel:
    def __init__(self, result_list: list) -> None:
        self.result_list = result_list
        
        self.init_retrieved_geotag = self.result_list[0].get_retrieved_image_list()[0]
        self.init_gps = self.init_retrieved_geotag.get_gps()
        self.init_name = self.init_retrieved_geotag.get_image_name_int()
        self.filtered_geotag = [self.init_retrieved_geotag]

        self.gaussian = namedtuple('Gaussian', ['mean', 'var'])
    
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
    
    # mean -> retireved top 1
    # variance -> top 1 <-> 나머지(2~9) 사이 거리 평균^2?
    def update(self, prior, measurement):
        # mean and variance
        x, P = prior
        z, R = measurement

        # residual
        y = z - x
        #Kalman gain
        K = 1 - P / (P + R)
        # print(f'K : {K}')
        #posterior
        x = x + K * y
        P = (1 - K) * P

        return self.gaussian(x, P)
    
    def predict(self, posterior, manuveur):
        # mean and variance
        x, P = posterior
        dx, Q = manuveur

        x = x + dx
        P = P + Q

        return self.gaussian(x, P)
    
    def KF_index(self):
        # retrieved에서 top1이 mean, top1과 나머지 retrieved 사이의 거리가 variance
        sensor_variance = self.variance_calculator(self.result_list[0].get_retrieved_image_list())
        process_variance = 10
        sensor_std = sqrt(sensor_variance)
        process_std = sqrt(process_variance)
        
        process_model = self.gaussian(1, process_variance)
        posterior = self.gaussian(self.init_name, sensor_variance)


        self.filtered_geotag.append(self.init_retrieved_geotag)
        # print(f'image name: {self.filtered_geotag[-1].get_image_name()}')

        for i in range(1, len(self.result_list)-1):
            prior = self.predict(posterior, process_model)
            # print(f'predict: {prior.mean}')
            retrieved_image_list = self.result_list[i].get_retrieved_image_list()
            
            process_variance = (retrieved_image_list[0].get_image_name_int() - prior.mean)**2

            variance = self.variance_calculator(retrieved_image_list)
            posterior = self.update(prior, self.gaussian(retrieved_image_list[0].get_image_name_int(), variance))
            
            # print(f'poseterior: {posterior.mean}')

            differ_index_list = [(posterior.mean - id.get_image_name_int())**2 for id in retrieved_image_list]
            min_val_idx = self.min_index(differ_index_list)
            self.filtered_geotag.append(retrieved_image_list[min_val_idx])


            # print(f'variance: {variance}, ?: {(retrieved_image_list[0].get_image_name_int() - prior.mean)**2}')
            if sqrt((retrieved_image_list[0].get_image_name_int() - prior.mean)**2) > 500:
                print(f'origin: {retrieved_image_list[0].get_image_name()}, predict: {prior.mean}, result: {self.filtered_geotag[-1].get_image_name()}')

            # print(f'image name: {self.filtered_geotag[-1].get_image_name()}')
            # print(f'mean: {posterior.mean}, variance:{posterior.var}')

    # 분산: 편차 제곱의 평균
    def variance_calculator(self, retireved_list: list) -> float:
        mean = retireved_list[0].get_image_name_int()
        
        square_error_sum = 0
        for i in range(len(retireved_list)):
            square_error_sum += (mean - retireved_list[i].get_image_name_int())**2

        variance = square_error_sum/len(retireved_list)
        # print(f'variance : {variance}')
        return variance

    def markov(self) -> None:
        for i in range(1, len(self.result_list)):
            retrieved_list = self.result_list[i].get_retrieved_image_list()
            
            # 직전 top1부터 현재 모든 리트리벌 결과(10개)들 사이의 거리
            distances = [self.gps_to_meter(self.filtered_geotag[-1].get_gps(), i.get_gps()) for i in retrieved_list]

            name_gap = [(self.filtered_geotag[-1].get_image_name_int() - i.get_image_name_int())**2 for i in retrieved_list]

            # print(distances)
            min_idx = self.min_index(distances)
            min_idx_name = self.min_index(name_gap)
            
            if int(distances[0]) > 50:
                self.filtered_geotag.append(retrieved_list[min_idx])
                # print(distances[0])
                # print(retrieved_list[min_idx])
            else:
                self.filtered_geotag.append(retrieved_list[0])

    def gt_filter(self) -> None:
        for i in range(1, len(self.result_list)):
            retrieved_list = self.result_list[i].get_retrieved_image_list()
            query = self.result_list[i].get_query()
            
            # 직전 top1부터 현재 모든 리트리벌 결과(10개)들 사이의 거리
            distances = [self.gps_to_meter(query.get_gps(), i.get_gps()) for i in retrieved_list]
            # print(distances)
            min_idx = self.min_index(distances)            
            self.filtered_geotag.append(retrieved_list[min_idx])

    def min_index(self, arr: list) -> int:
        idx = 0
        for i in range(len(arr)):
            if arr[idx] > arr[i]: idx = i

        return idx
    
    def get_filtered_geotag(self) -> list:
        self.markov()
        return self.filtered_geotag
    
    def get_kf_geotag(self) -> list:
        self.KF_index()
        return self.filtered_geotag
    
    def get_gt_filter(self) -> list:
        self.gt_filter()
        return self.filtered_geotag

def main():
    tmp = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

    for i, v in enumerate(tmp[1:]):
        print(f'i: {i}, v:{v}')

if __name__ == '__main__':
    main()