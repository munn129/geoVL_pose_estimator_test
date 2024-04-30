import numpy as np

# camera intrinsic parameter
# f_x 0 c_x 0 f_y c_y 0 0 1
K = np.array([1861.87717, 0, 982.67999,
              0, 1861.23669, 541.22597,
              0, 0, 1]).reshape((3,3))

# distortion coefficients
# k_1 k_2 p_1 p_2 k_3
distortion_coefficients = np.array([-0.33022, 0.31466, -0.00036, -0.00093, -0.34203])