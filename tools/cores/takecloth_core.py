import PIL.Image
import os
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

def run(input_file: str, output_file: str, message_callback=None):
    """
    脱衣服核心逻辑，仅处理单个文件
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径
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
            
    
            _, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            image, _ = LoadImageFromPath(input_file)
            image, rotation_info = SFAlignImageByFace(analysis_models, image, True, True, 10, False, None)
            segmenter = SFPersonSegmenterLoader()
            masks = SFPersonMaskGenerator(segmenter, image, True, False, True, True, True, 0.4, True)
            image2, masks, _, _, _ = SFImageScalerByPixels(image, 'lanczos', 2.0000000000000004, True, masks)
            image2, _, _, cutinfo = SFInpaintCutOut(image2, masks, 0, 0.20000000000000004, 'sdxl', 1, 0, 0, 0, 0)
            model, clip, vae = CheckpointLoaderSimple(r'xl\RealVisXL_V5.0_Lightning_fp16.safetensors')
            conditioning = SFAdvancedCLIPTextEncode('slim asian girl,(completely nude:1.6),(tiny breasts:1.25), Photorealism,Photomanipulation, detailed', clip, 'length+mean', 'A1111')
            conditioning2 = SFAdvancedCLIPTextEncode('(worst quality, low quality, illustration, 3d, 2d, painting, cartoons, sketch), cloth,open mouth', clip, 'length+mean', 'A1111')
            control_net = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
            control_net2 = SetUnionControlNetType(control_net, 'depth')
            image3 = DepthAnythingPreprocessor(image2, 'depth_anything_vits14.pth', 1024)
            positive, negative = ControlNetApplyAdvanced(conditioning, conditioning2, control_net2, image3, 0.25000000000000006, 0, 1, vae)
            control_net3 = SetUnionControlNetType(control_net, 'repaint')
            masks2 = SFPersonMaskGenerator(segmenter, image2, False, False, False, False, True, 0.4, True)
            masks2, _ = SFMaskChange(masks2, 0, 0.010000000000000002, False, 4, False)
            image4 = InpaintPreprocessor(image2, masks2, True)
            positive2, negative2 = ControlNetApplyAdvanced(positive, negative, control_net3, image4, 0.8500000000000002, 0, 1, vae)
            latent = VAEEncode(image2, vae)
            latent = KSampler(model, 17, 4, 2, 'dpmpp_sde', 'karras', positive2, negative2, latent, 1)
            image5 = VAEDecode(latent, vae)
            image5, _ = SFInpaintPaste(cutinfo, image5)
            image5 = SFRestoreRotatedImage(image5, rotation_info)
            images = util.get_images(image5)  # type: ignore
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
