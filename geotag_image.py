import cv2

class GeoTagImage:
    def __init__(self, image_path, gps_path):
        self.latitude = 0
        self.longitude = 0

        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if self.image is None: raise Exception("image is None")
        
        with open(gps_path, 'r') as file:
            for line in file:
                line = line.split()
                if line[0][-10:] == image_path[-10:]:
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