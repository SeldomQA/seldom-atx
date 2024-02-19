from matplotlib import pyplot as plt
import matplotlib
from dateutil import parser
import base64
from matplotlib import dates as mdates


def image_to_base64(image_path):
    """
    :param image_path:
    """
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        base64_data = base64.b64encode(image_bytes)
        base64_string = base64_data.decode("utf-8")
        return base64_string


def draw_chart(data_list, x_labels, line_labels, jpg_name='my_plt.jpg', label_title='Performance Chart',
               x_name='Time', y_name='Value'):
    """Draw a chart of performance data"""
    matplotlib.use('TkAgg')  # 使用 Tkinter 后端
    # 将元组列表中的数据按列提取到列表中
    data_cols = list(zip(*data_list))
    # 将时间字符串转换为 datetime 对象
    x_labels = [parser.parse(x) for x in x_labels]
    # 动态调整X轴的日期间隔和显示格式
    x_len = len(x_labels)
    x_locator = mdates.AutoDateLocator(minticks=x_len, maxticks=x_len)
    x_formatter = mdates.DateFormatter('%H:%M:%S')
    # 设置绘图窗口大小
    width = max(x_len, 25)
    plt.figure(figsize=(width, 10))
    # 设置 x 轴的日期定位器和格式化器
    plt.gca().xaxis.set_major_locator(x_locator)
    plt.gca().xaxis.set_major_formatter(x_formatter)
    # 针对每列数据绘制一条折线
    for i, data in enumerate(data_cols):
        plt.plot(x_labels, data, label=line_labels[i])
        for x, y in zip(x_labels, data):
            label = f'{y:.1f}'
            plt.annotate(label, xy=(x, y), xytext=(0, 5), textcoords='offset points')
    plt.xticks(rotation=45, ha='right')
    # 添加标题、标签和图例
    plt.title(label_title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.legend()
    # 保存为jpg格式图片
    plt.savefig(jpg_name, format='jpg')
    plt.close()  # 关闭图形窗口
    return image_to_base64(jpg_name)
