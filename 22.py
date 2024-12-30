import os
import cv2
import numpy as np
import random
import math
from tqdm import tqdm
import urllib.request

# 定义用户代理列表
agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1']

class ImageDownloader:
    def __init__(self, zoom, rootDir):
        self.zoom = zoom
        self.rootDir = rootDir
        self.proxies = {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890",
        }
        if not os.path.exists(rootDir):
            os.makedirs(rootDir)

    def deg2num(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        xtile_dot = (lon_deg + 180.0) / 360.0 * n - xtile
        ytile_dot = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n - ytile

        return (xtile, ytile),(xtile_dot,ytile_dot)

    def getimg(self, Tpath, Spath, x, y, max_retries=5):
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(Tpath, timeout=10) as response, open(Spath, 'wb') as f:
                    f.write(response.read())
                print(f"{x}_{y} 下载成功")
                return
            except Exception as e:
                print(f"{x}_{y} 下载失败，正在重试 ({attempt + 1}/{max_retries})")
        print(f"{x}_{y} 重试次数达到上限")

    def merge(self, x1, y1, x2, y2, x1_dot, y1_dot, x2_dot, y2_dot, z, path):
        print(x1, y1, x2, y2)
        row_list = []
        missing_images = []  # 记录缺失的图像
        for i in range(x1, x2 + 1):
            col_list = []
            for j in range(y1, y2 + 1):
                path_img = os.path.join(path, str(z), str(i), f"{j}.png")
                if os.path.isfile(path_img):
                    img = cv2.imread(path_img)
                    if img is not None:
                        col_list.append(img)
                    else:
                        print(f"无法读取图像：{path_img}")
                else:
                    missing_images.append(path_img)
            if col_list:
                k = np.vstack(col_list)
                row_list.append(k)
        if row_list:
            result = np.hstack(row_list)
            height, width = result.shape[:2] # 获取照片的高和宽

            x1_dot_p = x1_dot/(x2-x1+1)
            x2_dot_p = (x2_dot+x2-x1)/(x2-x1+1)
            y1_dot_p = y1_dot/(y2-y1+1)
            y2_dot_p = (y2_dot+y2-y1)/(y2-y1+1)

            left = int(width*x1_dot_p)
            right = int(width*x2_dot_p)
            top = int(height*y1_dot_p)
            bottom = int(height*y2_dot_p)

            accurate_result = result[top:bottom, left:right]
            cv2.imwrite(os.path.join(path, f"merge_{z}.png"), accurate_result)
            print(f"地图合并完成，保存为：{path}/merge_{z}.png")
        else:
            print("没有图像被合并，检查输入参数。")
        if missing_images:
            print("以下图像文件缺失：")
            for img in missing_images:
                print(img)

    def download(self, LTlat, LTlon, RBlat, RBlon):
        lefttop,lefttop_dot = self.deg2num(LTlat, LTlon, self.zoom)
        rightbottom,rightbottom_dot = self.deg2num(RBlat, RBlon, self.zoom)
        for x in range(lefttop[0], rightbottom[0] + 1):
            tile_path = os.path.join(self.rootDir, str(self.zoom), str(x))
            if not os.path.exists(tile_path):
                os.makedirs(tile_path)
            for y in range(lefttop[1], rightbottom[1] + 1):
                tile_url = f"https://www.google.com/maps/vt?lyrs=s&x={x}&y={y}&z={self.zoom}"
                tile_file = os.path.join(tile_path, f"{y}.png")
                if not os.path.isfile(tile_file):
                    self.getimg(tile_url, tile_file, x, y)

        print("开始合并地图...")
        self.merge(lefttop[0], lefttop[1], rightbottom[0], rightbottom[1],lefttop_dot[0], lefttop_dot[1], rightbottom_dot[0], rightbottom_dot[1], self.zoom, self.rootDir)

if __name__ == "__main__":
    # 示例参数，您需要根据实际情况替换
    zoom = 18
    rootDir = "./satellite"
    downloader = ImageDownloader(zoom, rootDir)

    google_output = 'LTlat=30.545917536790327+LTlon=114.35492685971069+RBlat=30.540207103808815+RBlon=114.36683586773681'
    url_spilt = google_output.split('+')
    url_params = {
        'LTlat': float(url_spilt[0][6:]),
        'LTlon': float(url_spilt[1][6:]),
        'RBlat': float(url_spilt[2][6:]),
        'RBlon': float(url_spilt[3][6:])
    }
    print(url_params)

    LT_lat, LT_lon, RB_lat, RB_lon = float(url_params['LTlat']), float(url_params['LTlon']), float(
        url_params['RBlat']), float(url_params['RBlon'])


    downloader.download(LT_lat, LT_lon, RB_lat, RB_lon)

