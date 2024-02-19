# 耗时
import cv2
import numpy as np
import os

from seldom_atx import AppConfig
from seldom_atx.logging import log


def extract_frames(video_file, output_dir, start_duration=AppConfig.FRAME_SECONDS,
                   end_duration=AppConfig.FRAME_SECONDS):
    """
    视频分帧
    :param video_file:
    :param output_dir:
    :param start_duration:
    :param end_duration:
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开视频文件
    cap = cv2.VideoCapture(video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    log.info("✅ 视频帧率为 {:.2f} fps/s.".format(fps))

    # 计算帧数和总时长（以秒为单位）
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_duration = total_frames / fps

    # 计算前5s片段的开始帧数和结束帧数
    start_frame = 0
    end_frame = int(fps * start_duration)

    # 如果末尾5s片段时长大于总时长，则设置为总时长
    if end_duration > total_duration:
        end_duration = total_duration

    # 计算末尾5s片段的开始帧数和结束帧数
    end_start_frame = total_frames - int(fps * end_duration)
    end_end_frame = total_frames

    # 初始化计数器和当前帧数
    frame_count = 0
    current_frame = 0

    # 循环读取视频帧
    while True:
        # 读取一帧
        ret, frame = cap.read()

        # 如果未读取到帧，则结束循环
        if not ret:
            break

        # 如果当前帧数在前5s或末尾5s范围内，则进行保存
        if start_frame <= current_frame < end_frame or end_start_frame <= current_frame < end_end_frame:
            # 生成输出文件名
            output_file = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")

            # 保存帧为图像文件
            cv2.imwrite(output_file, frame)

        # 更新计数器
        frame_count += 1

        # 更新当前帧数
        current_frame += 1

    # 释放视频对象
    cap.release()


def calculate_hash(image, hash_size=256):
    """Calculate the hash value of the input image"""
    # 将图像调整为指定大小，并转换为灰度图像
    image = cv2.resize(image, (hash_size, hash_size))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 计算均值
    mean = np.mean(gray)

    # 生成哈希值
    hash = []
    for i in range(hash_size):
        for j in range(hash_size):
            if gray[i, j] > mean:
                hash.append(1)
            else:
                hash.append(0)

    return hash


def get_image_diff(image1_path=None, image2_path=None, image1_hash=None, image2_hash=None):
    """
    计算当前图像和参考图像的哈希距离
    """
    if image1_hash:
        hash1 = image1_hash
    elif os.path.exists(image1_path):
        image = cv2.imread(image1_path)
        hash1 = calculate_hash(image)
    else:
        raise FileNotFoundError(f"No such file or directory: {image1_path}")
    if image2_hash:
        hash2 = image2_hash
    elif os.path.exists(image2_path):
        image = cv2.imread(image2_path)
        hash2 = calculate_hash(image)
    else:
        raise FileNotFoundError(f"No such file or directory: {image2_path}")
    distance = sum([a != b for a, b in zip(hash1, hash2)])
    return distance


def find_best_frame(reference_image_path, image_folder_path, is_start=True):
    """Find the image with the highest similarity to the reference image in the given image folder"""
    # 加载参考图像，并计算其哈希值
    reference_image = cv2.imread(reference_image_path)
    reference_hash = calculate_hash(reference_image)

    # 遍历图像文件夹中的所有图像，并计算它们的哈希值
    frame_path_list = os.listdir(image_folder_path)
    best_match = None
    best_distance = float('inf')
    if len(frame_path_list) <= int(AppConfig.FRAME_SECONDS * AppConfig.FPS) * 2:
        start_frame_num = len(frame_path_list) if is_start is True else 0
    else:
        start_frame_num = AppConfig.FRAME_SECONDS * AppConfig.FPS
    end_list = []
    for i, filename in enumerate(frame_path_list):
        if is_start and i < start_frame_num:
            if filename.endswith('.jpg'):
                path = os.path.join(image_folder_path, filename)
                distance = get_image_diff(image1_path=path, image2_hash=reference_hash)
                # 更新最相似的图像
                if distance <= best_distance or abs(best_distance - distance) < 100:
                    best_match = path
                    best_distance = distance

        elif not is_start and i >= start_frame_num:
            if filename.endswith('.jpg'):
                path = os.path.join(image_folder_path, filename)
                distance = get_image_diff(image1_path=path, image2_hash=reference_hash)
                # 更新最相似的图像
                if distance < best_distance:
                    best_match = path
                    best_distance = distance
                    end_list.append({'best_match': path, 'best_distance': distance})
    if not is_start:
        best_match_list = []
        for end in end_list:
            if abs(best_distance - end['best_distance']) < 100:
                best_match_list.append(end['best_match'])
        best_match = best_match_list[0]
    # 输出最相似的图像路径
    return best_match
