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
        self.image_name = str(image_path).split('/')[-1]
        
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
        if image.shape[0] == 0 or image.shape[1] == 0: raise Exception('image size is 0')

        # image 스케일을 줄이기 위한 코드
        # SIFT 과정 중 detectAndCompute()의 시간이 이미지의 사이즈에 따라 비례하기 때문.
        # 속도를 올리기 위해서는 이미지 사이즈를 줄여주는게 제일 효과적임
        if self.scale != 1:
            height, width = image.shape[:2]
            resized_image = cv2.resize(image, (int(width/self.scale), int(height/self.scale)))
            return resized_image
        else:
            return image
    
    # get_gps()로 위경도를 tuple로 반환할까 고민해봤지만,
    # 아무래도 호출에서 사용할 때 get_gps()[0] 보단 latitude라고 명시적으로 적혀 있는게 보기 좋을 것 같아서 분리함
    def get_latitude(self) -> float:
        return self.latitude
    
    def get_longitude(self) -> float:
        return self.longitude
    
    def get_azimuth(self) -> float:
        return self.azimuth

    def get_image_path(self) -> str:
        return self.image_path
    
    def get_scale(self) -> int:
        return self.scale
    
    # 그냥 이렇게 만드는게 맞는거같음. 너무 불편함
    def get_gps(self) -> tuple:
        return self.latitude, self.longitude
    
    def get_image_name(self) -> str:
        return self.image_name
    
    def get_image_name_int(self) -> int:
        return int(self.image_name[:-4])