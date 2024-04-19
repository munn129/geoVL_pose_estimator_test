'''
gt 값(list)과 estimation 값(list)을 입력받아,
각 요소별 오차(gps와 gps 사이 거리)를 계산하고, 저장하는 클래스
아직 수정해야 할 사항이 많음
'''

# TODO
# histogram
# scale에 따른 평가도 필요하려나

from math import pi, sin, cos, sqrt, atan2

class GeoError:
    def __init__(self, gps_1_list: list, gps_2_list: list, opt1 = '', opt2 = ''):
        self.gps_1_list = gps_1_list
        self.gps_2_list = gps_2_list
        if len(self.gps_1_list) != len(self.gps_2_list):
            raise Exception(f"The length of the input arguments(list) are different. \n \
                            gps_1_list: {len(self.gps_1_list)}, gps_2_list: {len(self.gps_2_list)}")
        
        # opt: What kind of gps(e.g., result of GPS, result of image retrieval, ...)
        self.opt1 = opt1
        self.opt2 = opt2

        self.error_list = []

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

        R = 6378.137 # radius of the earth in KM
        lat_to_deg = lat2 * pi/180 - lat1 * pi/180
        long_to_deg = lon2 * pi/180 - lon1 * pi/180

        a = sin(lat_to_deg/2)**2 + cos(lat1 * pi/180) * cos(lat2 * pi/180) * sin(long_to_deg/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c

        return d * 1000 #meter

    def _error_appender(self) -> None:
        for i in range(len(self.gps_1_list)):
            self.error_list.append(self._gps_to_meter(self.gps_1_list[i], self.gps_2_list[i]))
    
    def error_printer(self) -> None:
        self._error_appender()

        print('================================================')
        if self.opt1 != '' and self.opt2 != '':
            print(f'Error between {self.opt1} and {self.opt2}')

        error_sum = 0
        cnt = 0
        for gps_1, gps_2, error in zip(self.gps_1_list, self.gps_2_list, self.error_list):
            print(f'gps 1: {gps_1}')
            print(f'gps 2: {gps_2}')
            print(f'error: {error}[m]')
            error_sum += float(error)
            cnt += 1
        
        print(f'average of error {error_sum/cnt}')
        print('================================================')
