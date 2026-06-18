import sys
if "/www/adcitra/panel" not in sys.path:
    sys.path.insert(0, "/www/adcitra/panel")

if "/www/adcitra/panel/class" not in sys.path:
    sys.path.insert(0, "/www/adcitra/panel/class")

from adcitraDockerModel.dkgroupModel import main

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        group_id = sys.argv[1]
        status = sys.argv[2]
    else:
        print("参数错误")
        exit(1)

    main().group_status(group_id, status)


