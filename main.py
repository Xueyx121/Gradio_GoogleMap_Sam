import gradio as gr

# import sys
# sys.path.append(r'segment-anything')

import cv2
import matplotlib.pyplot as plt

from sam import segment_image



# 创建Gradio界面
interface = gr.Interface(
    fn=segment_image,
    inputs=gr.Image(type="pil"),
    outputs=gr.Image(type="pil"),
    live=True,
    title="SAM Image Segmentation",
    description="Upload an image to segment it using the Segment Anything Model (SAM)."
)

# 启动界面
# interface.launch()


def show_map():
    map_url = "https://www.google.com/maps/embed/v1/place?key=AIzaSyBFGRxkamVUdvQ4TtZfyIkVjuNkWP12T6o&q=30.53786,114.365248"  # 替换成你的经纬度
    iframe_html = f"""
    <iframe width="600" height="450" frameborder="0" style="border:0" 
    src="{map_url}" allowfullscreen></iframe>
    """
    return iframe_html


# 创建 Gradio 接口
def gradio_interface():
    with gr.Blocks() as demo:
        with gr.Row():
            gr.HTML("<h2>嵌入 Google 地图</h2>")

        # 显示地图
        map_output = gr.HTML(show_map(), label="嵌入地图")

    return demo


# 启动 Gradio 接口
gradio_interface().launch()

