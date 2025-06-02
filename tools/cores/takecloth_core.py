import PIL.Image
import os
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

def run(input_file: str, output_file: str, message_callback=None):
    """
    换脸核心逻辑，仅处理单个文件
    
    Args:
        char: 人脸LoRA名称
        input_file: 输入文件路径
        output_file: 输出文件路径
        sub_body: 是否去除身体
        message_callback: 消息回调函数 (message) -> None
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 检查输出文件是否已存在
    if os.path.exists(output_file):
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 已存在,跳过')
        return
    
    try:
        if message_callback:
            message_callback(f'开始处理: {os.path.basename(input_file)}')
            
        queue.watch_display(False)
        with Workflow():
            
    
            image, _ = LoadImageFromPath(input_file)
            segmenter = SFPersonSegmenterLoader()
            masks = SFPersonMaskGenerator(segmenter, image, True, False, False, True, True, 0.4000000000000001, True)
            masks, _ = SFMaskChange(masks, 0, 0.010000000000000002, False, 0, False)
            stitcher, cropped_image, _ = SFInpaintCrop(image, 'bilinear', 'bicubic', False, 'sd15', 1, False, 0, False, 0, 0, False, 1, 1, 1, 1, 1.2, '32', True, 'sdxl', 0.5, masks, None)
            model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
            model, clip = LoraLoader(model, clip, r'sdxl\m99_labiaplasty_pussy_2_sdxl.safetensors', 0.6000000000000001, 1.0000000000000002)
            conditioning = BNKCLIPTextEncodeAdvanced('slim asian girl,(completely nude:1.2),(tiny breasts:1.25), pussy,vagina,small breasts,small nipples,(no pubic hair , vaginal lips clearly visible:1.2),realistic, detailed', clip, 'length+mean', 'A1111')
            conditioning2 = BNKCLIPTextEncodeAdvanced('lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry', clip, 'length+mean', 'A1111')
            control_net = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
            control_net2 = SetUnionControlNetType(control_net, 'openpose')
            _, _, _, min_dimension, _ = SFGetImageSize(cropped_image)
            image2 = AIOPreprocessor(cropped_image, 'DWPreprocessor', min_dimension) # type: ignore
            positive, negative = ControlNetApplyAdvanced(conditioning, conditioning2, control_net2, image2, 0.8000000000000002, 0, 1, vae) # type: ignore
            control_net3 = SetUnionControlNetType(control_net, 'repaint')
            masks2 = SFPersonMaskGenerator(segmenter, cropped_image, False, False, False, False, True, 0.10000000000000002, True)
            masks2, _ = SFMaskChange(masks2, 0, 0.010000000000000002, False, 2, True)
            masks3 = SFPersonMaskGenerator(segmenter, cropped_image, True, False, True, True, False, 0.4000000000000001, True)
            masks3, _ = SFMaskChange(masks3, 0, -0.010000000000000002, False, 2, False)
            mask = MaskComposite(masks2, masks3, 0, 0, 'subtract')
            image3 = InpaintPreprocessor(cropped_image, mask, True)
            positive2, negative2 = ControlNetApplyAdvanced(positive, negative, control_net3, image3, 0.8000000000000002, 0, 1, vae)
            latent = VAEEncode(cropped_image, vae)
            latent = KSampler(model, 21, 4, 1, 'dpmpp_sde', 'karras', positive2, negative2, latent, 1)
            image4 = VAEDecode(latent, vae)
            image4 = SFInpaintStitch(stitcher, image4)
            images = util.get_images(image4)  # type: ignore
            images[0].save(output_file) # type: ignore
            
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise


if __name__ == '__main__':
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # 上层目录
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    run(r"D:\downloads\[小岛みなみ] 性感浑圆美胸让你脸红心跳 身材超辣 (36P)_dbee2fad\00021.webp", r'D:\正剧\tmp\output.png')
