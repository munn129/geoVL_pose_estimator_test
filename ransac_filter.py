from math import pi, sin, cos, sqrt, atan2

import cv2

from tqdm import tqdm

class RANSACFilter:
    def __init__(self, result_list: list) -> None:
        self.result_list = result_list
        self.filtered_geotag = []
        self.mask = []
        self.linear_gps = []

    def ransac_filter(self):

        for i in tqdm(range(len(self.result_list)), desc='sift'):
            sift_num = []
            retrieved_image = self.result_list[i]
            query = retrieved_image.get_query()
            retrieved_list = retrieved_image.get_retrieved_image_list()

            for j in retrieved_list:
                sift_num.append(self.sift_ransac(query.get_image(), j.get_image()))

            idx = self.max_index(sift_num)
            self.mask = self.weight_calculator(sift_num)
            self.filtered_geotag.append(retrieved_list[idx])

            # linear interpolation
            top1 = self.mask[0]
            top2 = self.mask[1]
            top3 = self.mask[2]
            lat = retrieved_list[top1].get_gps()[0] + retrieved_list[top2].get_gps()[0] + retrieved_list[top3].get_gps()[0]
            lon = retrieved_list[top1].get_gps()[1] + retrieved_list[top2].get_gps()[1] + retrieved_list[top3].get_gps()[1]
            self.linear_gps.append((lat/3, lon/3))
                

    def sift_ransac(self, query_image, retrieved_image) -> int:
        sift = cv2.SIFT_create()

        query_kp, query_des = sift.detectAndCompute(query_image, None)
        train_kp, train_des = sift.detectAndCompute(retrieved_image, None)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(query_des, train_des, k = 2)

        query_points = []
        train_points = []

        for i, (m,n) in enumerate(matches):
            if m.distance < 0.8 * n.distance:
                # if m.distance is under 0.5, error occurs
                query_points.append(query_kp[m.queryIdx].pt)
                train_points.append(train_kp[m.trainIdx].pt)

        return len(train_points)
    
    def max_index(self, arr: list) -> int:
        idx = 0
        for i in range(len(arr)):
            if arr[idx] < arr[i]: idx = i

        return idx
    
    def weight_calculator(self, arr:list) -> list:
        sorted_indices = sorted(range(len(arr)), key=lambda i: arr[i], reverse=True)

        return sorted_indices
    
    def get_ransac_filter(self):
        self.ransac_filter()
        return self.filtered_geotag
    
    def get_linear_interpolation(self):
        return self.linear_gps