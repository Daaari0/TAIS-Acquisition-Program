import ctypes
import time

FFLAG_ERRORALL = 0x00000001
FFLAG_HWPOSILMT = 0x00000002
FFLAG_HWNEGALMT = 0x00000004
FFLAG_SWPOGILMT = 0x00000008
FFLAG_SWNEGALMT = 0x00000010
FFLAG_RESERVED0 = 0x00000020
FFLAG_RESERVED1 = 0x00000040
FFLAG_ERRPOSOVERFLOW = 0x00000080
FFLAG_ERROVERCURRENT = 0x00000100
FFLAG_ERROVERSPEED = 0x00000200
FFLAG_ERRPOSTRACKING = 0x00000400
FFLAG_ERROVERLOAD = 0x00000800
FFLAG_ERROVERHEAT = 0x00001000
FFLAG_ERRBACKEMF = 0x00002000
FFLAG_ERRMOTORPOWER = 0x00004000
FFLAG_ERRINPOSITION = 0x00008000
FFLAG_EMGSTOP = 0x00010000
FFLAG_SLOWSTOP = 0x00020000
FFLAG_ORIGINRETURNING = 0x00040000
FFLAG_INPOSITION = 0x00080000
FFLAG_SERVOON = 0x00100000
FFLAG_ALARMRESET = 0x00200000
FFLAG_PTSTOPPED = 0x00400000
FFLAG_ORIGINSENSOR = 0x00800000
FFLAG_ZPULSE = 0x01000000
FFLAG_ORIGINRETOK = 0x02000000
FFLAG_MOTIONDIR = 0x04000000
FFLAG_MOTIONING = 0x08000000
FFLAG_MOTIONPAUSE = 0x10000000
FFLAG_MOTIONACCEL = 0x20000000
FFLAG_MOTIONDECEL = 0x40000000
FFLAG_MOTIONCONST = 0x80000000

SERVO_IN_BITMASK_LIMITP = 0x00000001
SERVO_IN_BITMASK_LIMITN = 0x00000002
SERVO_IN_BITMASK_ORIGIN = 0x00000004
SERVO_IN_BITMASK_CLEARPOSITION = 0x00000008
SERVO_IN_BITMASK_PTA0 = 0x00000010
SERVO_IN_BITMASK_PTA1 = 0x00000020
SERVO_IN_BITMASK_PTA2 = 0x00000040
SERVO_IN_BITMASK_PTA3 = 0x00000080
SERVO_IN_BITMASK_PTA4 = 0x00000100
SERVO_IN_BITMASK_PTA5 = 0x00000200
SERVO_IN_BITMASK_PTA6 = 0x00000400
SERVO_IN_BITMASK_PTA7 = 0x00000800
SERVO_IN_BITMASK_PTSTART = 0x00001000
SERVO_IN_BITMASK_STOP = 0x00002000
SERVO_IN_BITMASK_PJOG = 0x00004000
SERVO_IN_BITMASK_NJOG = 0x00008000
SERVO_IN_BITMASK_ALARMRESET = 0x00010000
SERVO_IN_BITMASK_SERVOON = 0x00020000
SERVO_IN_BITMASK_PAUSE = 0x00040000
SERVO_IN_BITMASK_ORIGINSEARCH = 0x00080000
SERVO_IN_BITMASK_TEACHING = 0x00100000
SERVO_IN_BITMASK_ESTOP = 0x00200000
SERVO_IN_BITMASK_JPTIN0 = 0x00400000
SERVO_IN_BITMASK_JPTIN1 = 0x00800000
SERVO_IN_BITMASK_JPTIN2 = 0x01000000
SERVO_IN_BITMASK_JPTSTART = 0x02000000
SERVO_IN_BITMASK_USERIN0 = 0x04000000
SERVO_IN_BITMASK_USERIN1 = 0x08000000
SERVO_IN_BITMASK_USERIN2 = 0x10000000
SERVO_IN_BITMASK_USERIN3 = 0x20000000
SERVO_IN_BITMASK_USERIN4 = 0x40000000
SERVO_IN_BITMASK_USERIN5 = 0x80000000
SERVO_IN_BITMASK_USERIN6 = 0x00000200
SERVO_IN_BITMASK_USERIN7 = 0x00000400
SERVO_IN_BITMASK_USERIN8 = 0x00000800


class EziServoPlusR:
    comPort = 0
    baudRate = 115200

    EziMotionPlusR = None

    def __init__(self, comPort, baudRate=115200):
        self.comPort = comPort
        self.baudRate = baudRate
        self.EziMotionPlusR = ctypes.cdll.LoadLibrary("./GMT_Stage_pkg/EziDrivers/EziMOTIONPlusRx64.dll")

    def connect(self):
        FAS_CONNECT = self.EziMotionPlusR.__getattr__("?FAS_Connect@@YAHEK@Z")
        FAS_CONNECT.argtypes = [ctypes.c_byte, ctypes.c_int]
        FAS_CONNECT.restype = ctypes.c_bool

        result = FAS_CONNECT(self.comPort, self.baudRate)
        return result

    def close(self):
        FAS_CLOSE = self.EziMotionPlusR.__getattr__("?FAS_Close@@YAXE@Z")
        FAS_CLOSE.argtypes = [ctypes.c_byte]
        FAS_CLOSE.restype = ctypes.c_void_p

        FAS_CLOSE(self.comPort)

    def moveToLimit(self, deviceNo, speed, direction):
        FAS_MoveToLimit = self.EziMotionPlusR.__getattr__("?FAS_MoveToLimit@@YAHEEKH@Z")
        FAS_MoveToLimit.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_uint32, ctypes.c_int]
        FAS_MoveToLimit.restype = ctypes.c_int

        FAS_MoveToLimit(self.comPort, deviceNo, speed, direction)

        time.sleep(1/1000)

        dwAxisStatus = self.getAxisStatus(deviceNo)

        while ((dwAxisStatus & FFLAG_MOTIONING) == FFLAG_MOTIONING):
            dwAxisStatus = self.getAxisStatus(deviceNo)
            time.sleep(1/1000)

    '''my codes start'''

    def setParameter(self, deviceNo, paramIndex, paramValue):
        """
        Set a parameter on the motor controller.
        :param deviceNo: Motor device number
        :param paramIndex: Index of the parameter to set (check manual)
        :param paramValue: Value to assign to the parameter (check manual)
        """
        FAS_SetParameter = self.EziMotionPlusR.__getattr__("?FAS_SetParameter@@YAHEEEJ@Z")
        FAS_SetParameter.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_uint32, ctypes.c_uint32]
        FAS_SetParameter.restype = ctypes.c_int

        result = FAS_SetParameter(self.comPort, deviceNo, paramIndex, paramValue)
        if result != 0:
            print(f"Error setting parameter {paramIndex} to {paramValue} (error code {result})")
        else:
            print(f"Parameter {paramIndex} successfully set to {paramValue} for device {deviceNo}")

    def setOriginAtLowerLimit(self, deviceNo, speed):
        """
        Move to the negative limit and set that position as origin (zero).
        :param deviceNo: Motor device number
        :param speed: Speed to reach the limit
        """
        # Step 1: Move to the negative limit
        self.moveToLimit(deviceNo, speed, direction=0)  # 0 = negative direction

        # Step 2: Clear position (set current position as origin)
        FAS_ClearPosition = self.EziMotionPlusR.__getattr__("?FAS_ClearPosition@@YAHEE@Z")
        FAS_ClearPosition.argtypes = [ctypes.c_byte, ctypes.c_byte]
        FAS_ClearPosition.restype = ctypes.c_int

        result = FAS_ClearPosition(self.comPort, deviceNo)
        if result != 0:
            print(f"Error: Failed to clear position at lower limit (error code {result})")
        else:
            print(f"Origin successfully set at lower limit for device {deviceNo}")

    def moveToOrigin(self, deviceNo):
        """
        Move a specific axis to its origin.
        NOTE: it also somehow redefines the origin to the lower limit. dont know why
        """
        FAS_MoveOriginSingleAxis = self.EziMotionPlusR.__getattr__("?FAS_MoveOriginSingleAxis@@YAHEE@Z")
        FAS_MoveOriginSingleAxis.argtypes = [ctypes.c_byte, ctypes.c_byte]
        FAS_MoveOriginSingleAxis.restype = ctypes.c_int

        result = FAS_MoveOriginSingleAxis(self.comPort, deviceNo)
        if result != 0:
            print(f"Error: Failed to move axis {deviceNo} to origin (error code {result})")

        # Optional: Wait until motion completes
        time.sleep(1/1000)
        dwAxisStatus = self.getAxisStatus(deviceNo)
        while (dwAxisStatus & FFLAG_MOTIONING) == FFLAG_MOTIONING:
            dwAxisStatus = self.getAxisStatus(deviceNo)
            time.sleep(1/1000)

    def moveToPosition(self, deviceNo, position, speed):
        """
        Move the stage to a specific absolute position.
        :param deviceNo: Motor device number
        :param position: Target position in pulses
        :param speed: Movement speed
        """
        FAS_MoveSingleAxisAbsPos = self.EziMotionPlusR.__getattr__("?FAS_MoveSingleAxisAbsPos@@YAHEEJK@Z")
        FAS_MoveSingleAxisAbsPos.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_int, ctypes.c_uint]
        FAS_MoveSingleAxisAbsPos.restype = ctypes.c_int

        result = FAS_MoveSingleAxisAbsPos(self.comPort, deviceNo, position, speed)

        if result != 0:
            print(f"Error: Failed to move to position {position} (error code {result})")

        # Wait until motion completes
        time.sleep(1/1000)
        dwAxisStatus = self.getAxisStatus(deviceNo)

        while (dwAxisStatus & FFLAG_MOTIONING) == FFLAG_MOTIONING:
            dwAxisStatus = self.getAxisStatus(deviceNo)
            time.sleep(1/1000)

    def setActualPosition(self, deviceNo, value):
        FAS_SetActualPos = self.EziMotionPlusR.__getattr__("?FAS_SetActualPos@@YAHEEJ@Z")
        FAS_SetActualPos.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_long]
        FAS_SetActualPos.restype = ctypes.c_int

        result = FAS_SetActualPos(self.comPort, deviceNo, value)
        if result != 0:
            print(f"Error setting actual position (error code {result})")
        else:
            print(f"Actual position set to {value} for device {deviceNo}")

    def getActualPosition(self, deviceNo):  # doesnt work
        pos = ctypes.c_long(0)
        FAS_GetActualPos = self.EziMotionPlusR.__getattr__("?FAS_GetActualPos@@YAHEEPEAJ@Z")
        FAS_GetActualPos.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.POINTER(ctypes.c_long)]
        FAS_GetActualPos.restype = ctypes.c_int

        result = FAS_GetActualPos(self.comPort, deviceNo, ctypes.byref(pos))
        if result != 0:
            print(f"Error reading position (error code {result})")
            return None
        return pos.value

    def getCommandPosition(self, deviceNo):
        """
        Retrieve the commanded position of the axis (in pulses).
        This reflects the target position the controller is trying to reach.
        """
        pos = ctypes.c_long(0)
        FAS_GetCommandPos = self.EziMotionPlusR.__getattr__("?FAS_GetCommandPos@@YAHEEPEAJ@Z")
        FAS_GetCommandPos.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.POINTER(ctypes.c_long)]
        FAS_GetCommandPos.restype = ctypes.c_int

        result = FAS_GetCommandPos(self.comPort, deviceNo, ctypes.byref(pos))
        if result != 0:
            print(f"Error reading command position (error code {result})")
            return None
        return pos.value
    '''my codes end'''

    def getAxisStatus(self, deviceNo):
        dwStatus = (ctypes.c_uint32)(0)
        dwStatusPtr = ctypes.POINTER(ctypes.c_uint)(dwStatus)

        FAS_GetAxisStatus = self.EziMotionPlusR.__getattr__("?FAS_GetAxisStatus@@YAHEEPEAK@Z")
        FAS_GetAxisStatus.argtypes = [ctypes.c_byte, ctypes.c_byte, ctypes.c_void_p]
        FAS_GetAxisStatus.restype = ctypes.c_int

        FAS_GetAxisStatus(self.comPort, deviceNo, dwStatusPtr)

        return dwStatus.value
