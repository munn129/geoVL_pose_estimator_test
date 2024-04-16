import cv2

class GeoTagImage:
    def __init__(self, image_path, gps_path):
        self.latitude = 0
        self.longitude = 0
        self.azimuth = 0

        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if self.image is None: raise Exception("image is None")
        
        # read gps
        with open(gps_path, 'r') as file:
            for line in file:
                line = line.split()
                # image retrieval 결과에 있는 이미지와 gps list에 있는 이미지의 이름이 같을 때
                if str(line[0]).split('/')[-1] == str(image_path).split('/')[-1]:
                    self.latitude = float(line[1])
                    self.longitude = float(line[2])
                    break
        if self.latitude == 0 or self.longitude == 0: raise Exception("gps is zero")

    def get_image(self):
        return self.image
    
    def get_latitude(self):
        return self.latitude
    
    def get_longitude(self):
        return self.longitude
    
    def get_azimuth(self):
        return self.azimuth