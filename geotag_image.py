'''
Image와 GPS, Azimuth 값을 저장하는 클래스
Image는 경로만 저장하며, get_image() 호출 시 이미지를 읽는다.
'''

import cv2

class GeoTagImage:
    def __init__(self, image_path, gps_path):
        self.latitude = 0
        self.longitude = 0
        self.azimuth = 0
        self.image_path = image_path
        
        # read gps
        with open(gps_path, 'r') as file:
            for line in file:
                line = line.split()
                # image retrieval 결과에 있는 이미지와 gps list에 있는 이미지의 이름이 같을 때
                if str(line[0]).split('/')[-1] == str(image_path).split('/')[-1]:
                    self.latitude = float(line[1])
                    self.longitude = float(line[2])
                    self.azimuth = float(line[3])
                    break
        if self.latitude == 0 or self.longitude == 0 or self.azimuth == 0:
            raise Exception("Wrong GPS or azimuth value")

    def get_image(self):
        image = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
        if self.image is None: raise Exception("image is None")
        return image
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_azimuth(self):
        return self.azimuth
