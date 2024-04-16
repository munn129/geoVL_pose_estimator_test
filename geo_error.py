from math import pi, sin, cos, sqrt, atan2

# Todo
# 생각해보니, 여기서  GeoTagImage class를 입력 받아야 함
class GeoError:
    def __init__(self, gps_1_list, gps_2_list, opt1 = '', opt2 = ''):
        self.gps_1_list = gps_1_list
        self.gps_2_list = gps_2_list
        if len(self.gps_1_list) != len(self.gps_2_list):
            raise Exception("The length of the input arguments(list) are different.")
        
        # opt: What kind of gps(e.g., result of GPS, result of image retrieval, ...)
        self.opt1 = opt1
        self.opt2 = opt2

        self.error_list = []

    def _gps_to_meter(self, gps_1, gps_2) -> float:
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

        for gps_1, gps_2, error in zip(self.gps_1_list, self.gps_2_list, self.error_list):
            print(gps_1)
            print(gps_2)
            print(f'error: {error}[m]')
        
        print('================================================')