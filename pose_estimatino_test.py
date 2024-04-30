import os
import cv2
import numpy as np

from pose_estimation import PoseEstimation

def main():
    root_dir = '../../patchnetvlad_workspace/data'
    query_dir = '0404_full'
    query_img = '000005.png'
    db_dir = '1024_1m'
    db_img = '002305.png'
    scale = 5

    img1_dir = os.path.join(root_dir, query_dir, query_img)
    img2_dir = os.path.join(root_dir, db_dir, db_img)

    img1 = cv2.imread(img1_dir)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    h, w = img1.shape[:2]
    print(f'h: {h}, w: {w}')
    img1_resized = cv2.resize(img1, (int(w/scale), int(h/scale)))

    img2 = cv2.imread(img2_dir)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img2_resized = cv2.resize(img2, (int(w/scale), int(h/scale)))

    pose_estimation = PoseEstimation()

    # rt_mat = pose_estimation.rt_calculator(img1_resized, img2_resized)
    rt_mat = rt_calculator(img1_resized, img2_resized)


    print(rt_mat)


def rt_calculator(query_image, retrieved_image, image_name = ''):
        '''
        input
        query_image: np.array
        retrieved_image: np.array
        output
        rt_matrix: 4*4 homogeneous np.array
        '''
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

        query_points = np.int32(query_points)
        train_points = np.int32(train_points)

        E, mask = cv2.findEssentialMat(query_points, train_points)
    
        retval, rot, tran, mask = cv2.recoverPose(E, query_points, train_points)
        
        rt_matrix = np.eye(4)

        rt_matrix[:3, :3] = rot
        rt_matrix[:3, 3] = tran.T
        rt_matrix[3,3] = 1

        return rt_matrix

if __name__ == '__main__':
    main()
