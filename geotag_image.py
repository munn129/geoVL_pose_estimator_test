'''
Image와 GPS, Azimuth 값을 저장하는 클래스
Image는 경로만 저장하며, get_image() 호출 시 이미지를 읽는다.
'''

import os

import cv2

class GeoTagImage:
    def __init__(self, image_path: str, gps_path: str, idx: int, scale = 1, image_path_prefix = ''):
        self.latitude = 0
        self.longitude = 0
        self.azimuth = 0
        self.image_path = image_path
        self.scale = scale
        self.image_path_prefix = image_path_prefix
        
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
            raise Exception(f"Wrong GPS or azimuth value. idx: {idx}, image_path: {image_path}, gps_path: {gps_path}")

    def get_image(self):
        if self.image_path_prefix != '': image_path = os.path.join(self.image_path_prefix, self.image_path)
        else: image_path = self.image_path
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if image is None: raise Exception("image is None")

        # image 스케일을 줄이기 위한 코드
        # SIFT 과정 중 detectAndCompute()의 시간이 이미지의 사이즈에 따라 비례하기 때문.
        # 속도를 올리기 위해서는 이미지 사이즈를 줄여주는게 제일 효과적임
        if self.scale != 1:
            height, width = image.shape[:2]
            resized_image = cv2.resize(image, (int(width/self.scale), int(height/self.scale)))
            return resized_image
        else:
            return image
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_azimuth(self):
        return self.azimuth
