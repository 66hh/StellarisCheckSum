import os
import json
import hashlib

def list_dir(path, suffix, sub):

    result = []

    # 排序同步游戏的文件搜索顺序
    files = sorted(os.listdir(path))
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            if file_path.endswith(suffix):
                result.append(file_path)
        elif os.path.isdir(file_path) and sub:
            result += list_dir(file_path, suffix, sub)
    
    return result

def load_manifest(path):

    files = []

    read = -1
    
    name = ""
    sub_directories = ""
    file_extension = ""

    # 从checksum_manifest中加载hash计算范围
    for line in open(os.path.join(path, "checksum_manifest.txt"), 'r'):
        data = line.strip()

        if data == "directory" and read <= 0:
            read = 3
        
        if data.startswith("name") and read != 0:
            read -= 1
            name = data.split("=")[1].strip()
        
        if data.startswith("sub_directories") and read != 0:
            read -= 1
            sub_directories = data.split("=")[1].strip()
        
        if data.startswith("file_extension") and read != 0:
            read -= 1
            file_extension = data.split("=")[1].strip()
        
        # 如果三个参数都读取齐了就开始统计文件
        if read == 0:
            read = -1
            files += list_dir(os.path.join(path, name), file_extension, sub_directories == "yes")

    return files

def get_version(path):
    # 通过启动器json读取版本
    data = open(os.path.join(path, "launcher-settings.json"), 'r', encoding="utf8")
    return "Circinus " + json.load(data)["rawVersion"].strip()

def get_full_version(path):
    # 通过启动器json读取版本
    data = open(os.path.join(path, "launcher-settings.json"), 'r', encoding="utf8")
    return json.load(data)["version"].strip()

def calc_checksum(path):
    files = load_manifest(path)
    version = get_version(path)

    md5 = hashlib.md5()

    for file in files:
        md5.update(open(file, 'rb').read())

        # 计算相对路径
        dir = os.path.relpath(file, path)
        dir = dir.replace("\\", "/")

        md5.update(dir.encode("utf8"))

    md5.update(version.encode("utf8"))

    return md5.hexdigest()

gamepath = input("gamepath: ")
print("version: %s" % get_full_version(gamepath))
print("checksum: %s" % calc_checksum(gamepath))
