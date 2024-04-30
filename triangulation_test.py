from math import asin, pi, cos, sin, sqrt
import numpy as np

def compute_angle_between_vectors(vec_1, vec_2):
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

def triangle_gps_estimate(alpha, beta, gamma, d):
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
    d = 1
    vec_1 = np.array([0.5, -sqrt(3)/2])
    vec_2 = np.array([1.5, -sqrt(3)/2])

    alpha = compute_angle_between_vectors(vec_1, vec_2)

    vec_3 = vec_1 - vec_2
    beta = compute_angle_between_vectors(vec_1, vec_3)

    gamma = pi - beta - alpha

    x, y = triangle_gps_estimate(alpha, beta, gamma, d)

    print(x, y)
    print(alpha * 180 / pi)
    print(beta * 180 / pi)
    print(gamma * 180 / pi)

if __name__ == '__main__':
    main()