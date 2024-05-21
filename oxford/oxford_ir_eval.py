from math import pi, sin, cos, sqrt, atan2

from tqdm import tqdm

def gps_to_meter(gps_1: tuple, gps_2: tuple) -> float:
        '''
        input
        - gps_1: tuple(latitude, longitude)
        - gps_2: tuple(latitude, longitude)
        output
        - distance of between gps_1 and gps_2 [m]
        '''
        lat1, lon1 = gps_1
        lat2, lon2 = gps_2

        # 지구의 넓이 반지름
        R = 6371.0072 # radius of the earth in KM
        lat_to_deg = lat2 * pi/180 - lat1 * pi/180
        long_to_deg = lon2 * pi/180 - lon1 * pi/180

        a = sin(lat_to_deg/2)**2 + cos(lat1 * pi/180) * cos(lat2 * pi/180) * sin(long_to_deg/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c

        return d * 1000 #meter

def main():
    result = 'NetVLAD_predictions_oxford.txt'
    q_gps = '151110gps.txt'
    i_gps = '151113gps.txt'
    
    eval_result = 'oxford_netvlad.txt'

    q_name_list = []
    i_name_list = []

    with open(result, 'r') as file:
        for line in file:
            if line[0] == '#': continue

            line = line.split('\n')[0]
            line = line.split(', ')
            
            q_name_list.append(line[0][1:])
            i_name_list.append(line[1][1:])

    q_gps_list = []

    for img_path in tqdm(q_name_list):
        with open(q_gps, 'r') as file:
            for line in file:
                line = line.split()
                if str(line[0]).split('/')[-1] == str(img_path).split('/')[-1]:
                    q_gps_list.append((float(line[1]), float(line[2])))
    i_gps_list = []
    
    for img_path in tqdm(i_name_list):
        with open(i_gps, 'r') as file:
            for line in file:
                line = line.split()
                if str(line[0]).split('/')[-1] == str(img_path).split('/')[-1]:
                    i_gps_list.append((float(line[1]), float(line[2])))

    with open(eval_result, 'w') as file:
        file.write('# translation error\n')

    cnt = 0
    total_err = 0
    for i in range(len(q_gps_list) - 1):
        cnt += 1
        gap = gps_to_meter(q_gps_list[i], i_gps_list[i])
        with open(eval_result, 'a') as file:
            file.write(f'{gap}\n')
        total_err += gap

    print(total_err/cnt)

if __name__ == '__main__':
    main()