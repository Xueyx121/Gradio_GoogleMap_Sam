import torch
from PIL import Image
import numpy as np
from segment_anything import sam_model_registry, SamPredictor

# 图片分割
def segment_image(input_image: Image.Image):
    # 检查是否有可用的 GPU
    sam_device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {sam_device}")

    # 加载SAM模型
    sam_model_path = "sam_vit_l_0b3195.pth"  # 替换为你实际的模型路径
    # sam_model = SamModel.from_checkpoint(sam_model_path)
    sam_model = sam_model_registry["vit_l"](checkpoint=sam_model_path)
    sam_model = sam_model.to(device=sam_device)
    sam_predictor = SamPredictor(sam_model)

    # 将PIL图像转换为numpy数组
    image = np.array(input_image)

    # 将图像数据转移到GPU（如果有GPU）
    sam_predictor.set_image(image)

    masks, _, _ = sam_predictor.predict(point_coords=None, point_labels=None, multimask_output=False)

    # 将掩码转换为PIL图像
    mask_image = Image.fromarray(masks[0] * 255)  # 假设只使用第一个掩码
    return mask_image