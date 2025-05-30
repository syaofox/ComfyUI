import PIL.Image
import os
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

def run(char: str, input_file: str, output_file: str, repaint_hair: bool = True, 
        message_callback=None):
    """
    换脸核心逻辑，仅处理单个文件
    
    Args:
        char: 人脸LoRA名称
        input_file: 输入文件路径
        output_file: 输出文件路径
        repaint_hair: 是否重绘头发
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
            instantid = InstantIDModelLoader('ip-adapter.bin')
            faceanalysis = InstantIDFaceAnalysis('CUDA')
            control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            lora, image = HyperLoRALoadCharLoRA(char)
            model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
            model = HyperLoRAApplyLoRA(model, lora, 0.85)
            clip2 = CLIPSetLastLayer(clip, -2)
            conditioning = BNKCLIPTextEncodeAdvanced('fcsks fxhks fhyks,a beautiful girl, Look at the camera, Real photography, 4K, RAW photo, close-up, exquisite makeup, delicate skin,  real photos, best picture quality, high details', clip2, 'length+mean', 'A1111')
            conditioning2 = BNKCLIPTextEncodeAdvanced('finger,hande,lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet', clip2, 'length+mean', 'A1111')
            analysis_models = FaceAnalysisModels('insightface', 'CUDA')
            image2, _ = LoadImageFromPath(input_file)
            image2, _, _, _, _ = ImageScalerByPixels(image2, 'lanczos', 2.8000000000000007, True, None)
            image2, _, inverse_rotation_angle = AlignImageByFace(analysis_models, image2, True, False, None)
            image2, bounding_info = FaceCutout(analysis_models, image2, 0, 0.5000000000000001, -1, 'sdxl', 1)
            model, positive, negative = ApplyInstantIDAdvanced(instantid, faceanalysis, control_net, image, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', image2, None)
            latent = VAEEncode(image2, vae)
            latent = KSamplerAdvanced(model, 'enable', 100006, 4, 1.4000000000000001, 'dpmpp_sde', 'karras', positive, negative, latent, 1, 2, 'disable')
            image3 = VAEDecode(latent, vae)
            warped_image = FaceMorph(image2, image3, 'OUTLINE', 'Landmarks', 'CPU')
            latent2 = VAEEncode(warped_image, vae)
            masks = APersonMaskGenerator(warped_image, True, False, repaint_hair, False, False, 0.20000000000000004, True)
            latent2 = SetLatentNoiseMask(latent2, masks)
            latent2 = KSamplerAdvanced(model, 'enable', 100007, 8, 1.2, 'dpmpp_sde', 'karras', positive, negative, latent2, 4, 8, 'disable')
            image4 = VAEDecode(latent2, vae)
            image5 = ImageColorMatch(image4, image4, 'RGB', 1, 'auto', 0, None)
            image5, _ = FacePaste(image5, bounding_info, 0, 0.05000000000000001, 20)
            image5 = ImageRotate(image5, inverse_rotation_angle, True)
            image5 = TrimImageBorders(image5, 10)
            images = util.get_images(image5)
            images[0].save(output_file)
            
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise 