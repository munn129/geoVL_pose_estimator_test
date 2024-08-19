import numpy as np
from math import asin, pi, sqrt, cos, sin

class Triangulation:
    def __init__(self) -> None:
        pass

    # 사실 pose_estimation에 있는 함수랑 동일함.
    def scale_calculator(self, query_latitude, query_longitude, train_lattitude, train_longitude):
        '''
        input
        all float
        output
        scale: float
        '''
        return sqrt((query_latitude - train_lattitude)**2 + (query_longitude - train_longitude)**2)

    def homogeneous_to_2d_vector(self, homogeneous):
        '''
        input
        homogeneous matrix
        ouput
        1*2 vector (np.array())
        '''
        # Homogeneous 행렬에서 translation부분의 x값과 y값만 가져와서 2*1 행렬로 만듦
        return np.array(homogeneous[:2,3]).T
    
    def compute_angle_between_vectors(self, vec_1, vec_2):
        '''
        input
        two vector(1*2)
        ouput
        angle between two vectors (rad)
        '''
        # outer product, |a||b|sin(theta)
        cross_product_result = np.cross(vec_1, vec_2)
        
        # theta = sin^(-1)(|a x b|/(|a||b|))
        theta = asin(np.linalg.norm(cross_product_result) / (np.linalg.norm(vec_1) * np.linalg.norm(vec_2)))
        
        return theta
    
    def triangle_angle(self, alpha, beta):
        '''
        input
        alpha, gamma: rad
        output
        beta: rad
        '''
        return pi - alpha - beta
    
    def triangle_angle(self, alpha, beta):
        '''
        input
        alpha, gamma: rad
        output
        beta: rad
        '''
        return pi - alpha - beta
    
    def triangle_gps_estimate(self, alpha, beta, gamma, d):
        '''
        input
        alpha ~ gamma: rad
        d: distance of two images(gps scale)
        ouput
        tuple (x,y)
        x: latitude compensation
        y: longitude compenstaion
        '''
        tmp = gamma * d / alpha
        x = tmp * cos(beta)
        y = tmp * sin(beta)
        return x, y
    
def main():
    t = Triangulation()

    d = 1
    vec_1 = np.array([0.5, -sqrt(3)/2])
    vec_2 = np.array([1.5, -sqrt(3)/2])

    alpha = t.compute_angle_between_vectors(vec_1, vec_2)

    vec_3 = vec_1 - vec_2
    beta = t.compute_angle_between_vectors(vec_1, vec_3)

    gamma = pi - beta - alpha

    x, y = t.triangle_gps_estimate(alpha, beta, gamma, d)

    print(x, y)
    print(alpha * 180 / pi)
    print(beta * 180 / pi)
    print(gamma * 180 / pi)

if __name__ == '__main__':
    main()