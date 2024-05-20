from oxford_ir_eval import gps_to_meter

def main():
    gps = '151113gps.txt'
    gps_list = []

    with open(gps, 'r') as file:
        for line in file:
            line = line.split()
            if line[0] == '#': continue
            # print(line)
            gps_list.append((float(line[1]), float(line[2])))

    # print(gps_list)

    distance = 0
    cnt = 0
    for i in range(len(gps_list) -1):
        gap = gps_to_meter(gps_list[i], gps_list[i+1])
        if gap > 50: cnt += 1
        distance += gap

    print(f'dataset distance : {distance/(len(gps_list) - 1)}')
    print(cnt)

if __name__ == '__main__':
    main()