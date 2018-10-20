import matplotlib.pyplot as plt
from time import sleep
import console
import motion

import location # GPS

from objc_util import ObjCInstance, ObjCClass, ObjCBlock, c_void_p

relativeAltitude = 0.0

def altimeterHandler(_cmd, _data, _error):
    global relativeAltitude
    relativeAltitude = ObjCInstance(_data).relativeAltitude().floatValue()

handler_block = ObjCBlock(altimeterHandler, restype=None,
                          argtypes=[c_void_p, c_void_p, c_void_p])

def main():
    num_samples = 1000000
    arrayA = []
    arrayM = []
    #arrayG = []
    arrayP = []
    arrayJ=[]
    arrayGPS = [] #GPS
    dataArray = []

    CMAltimeter = ObjCClass('CMAltimeter')
    NSOperationQueue = ObjCClass('NSOperationQueue')
    if not CMAltimeter.isRelativeAltitudeAvailable():
        print('This device has no barometer.')
        return
    altimeter = CMAltimeter.new()
    main_q = NSOperationQueue.mainQueue()
    altimeter.startRelativeAltitudeUpdatesToQueue_withHandler_(main_q, handler_block)
    motion.start_updates()
    location.start_updates() # GPS
    print("Logging start...")
    sleep(1.0)
    for i in range(num_samples):
        sleep(0.05)
        a = motion.get_user_acceleration()
        m = motion.get_magnetic_field()
        j = motion.get_attitude()
        gps = location.get_location() # GPS
        if a[1] > 0.8:
        	break
        dataArray.append([relativeAltitude,a[2],m[0],m[1]])
        arrayA.append(a)
        arrayM.append(m)
        arrayJ.append(j)
        arrayP.append(relativeAltitude)
        arrayGPS.append(gps)  #GPS

    motion.stop_updates()
    location.stop_updates() # GPS
    altimeter.stopRelativeAltitudeUpdates()
    print("Logging stop and Saving start...")
    import pickle
    f = open('yokohama.serialize','wb')
    #pickle.dump([arrayA, arrayM, arrayP],f)
    pickle.dump([arrayA, arrayM, arrayJ, arrayP, arrayGPS],f) #GPS
    f.close
    print("Saving is finished.")
    x_values = [x*0.05 for x in range(len(dataArray))]
    for i, color, label in zip(range(3), 'rgb', 'XYZ'):
        plt.plot(x_values, [g[i] for g in arrayM], color, label=label, lw=2)
    plt.grid(True)
    plt.xlabel('t')
    plt.ylabel('G')
    plt.gca().set_ylim([-100, 100])
    plt.legend()
    plt.show()

if __name__ == '__main__':
	main()

