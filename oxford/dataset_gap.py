from oxford_ir_eval import gps_to_meter

def main():
    gps = 'oxford_151110_gps.txt'
    gps_list = []

    with open(gps, 'r') as file:
        for line in file:
            line = line.split()
            gps_list.append((float(line[1]), float(line[2])))

    print(gps_list)

    distance = 0
    for i in range(len(gps_list) -1):
        distance += gps_to_meter(gps_list[i], gps_list[i+1])

    print(f'dataset distance : {distance/(len(gps_list) - 1)}')

if __name__ == '__main__':
    main()