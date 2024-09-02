import ctypes
import os

# 加载DLL
dll = ctypes.windll.LoadLibrary('walkfree.dll')

# 定义函数的参数和返回类型
dll.WriteHeader.argtypes = [ctypes.c_char_p, ctypes.c_int]
dll.WriteHeader.restype = ctypes.c_int

dll.WriteImage.argtypes = [ctypes.c_char_p, ctypes.c_int]
dll.WriteImage.restype = ctypes.c_int

# 第3个参数是音质(1-6 不能为4 1代表高音质 2代表立体声 3代表高音质一般音频 5为中等 6为低音质)
dll.WriteMusic.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
dll.WriteMusic.restype = ctypes.c_int

# 调用函数
path = b"test1.gba"
unknown_value = 0x1  # 替换为适当的整数值
result = dll.WriteHeader(path, unknown_value)

# 检查结果
if result == 0:
    print("Header written successfully.")
else:
    print("Failed to write header.")

path = b"temp1.bmp"  # 路径需要为字节字符串
result = dll.WriteImage(path, 1)

print(os.path.getsize("test1.gba"))

# 检查结果
if result == 0:
    print("Image written successfully.")
else:
    print("Failed to write Image.")

# 调用函数
path = b"temp2.wav"  # 路径需要为字节字符串
result = dll.WriteMusic(path, 1, 6, 0, 0)

print(os.path.getsize("test1.gba"))

# 检查结果
if result == 0:
    print("Music written successfully.")
else:
    print("Failed to write music.")
