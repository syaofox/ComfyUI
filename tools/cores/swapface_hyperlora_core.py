import os
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *


def load_models():
    """加载所需的模型"""
    insightface_model, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
    instantid = InstantIDModelLoader('ip-adapter.bin')
    control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
    occluder = SFOccluderLoader('xseg_3')
    control_net2 = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
    control_net2 = SetUnionControlNetType(control_net2, 'canny/lineart/anime_lineart/mlsd')
    
    return {
        'analysis_models': analysis_models,
        'insightface_model': insightface_model,
        'instantid': instantid,
        'control_net': control_net,
        'occluder': occluder,
        'control_net2': control_net2
    }


def load_character_and_base_models(char):
    """加载角色LoRA和基础模型"""
    lora, char_image = HyperLoRALoadCharLoRA(char)
    model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
    model = HyperLoRAApplyLoRA(model, lora, 0.85)
    clip = CLIPSetLastLayer(clip, -2)
    
    return model, clip, vae, char_image


def preprocess_image(models, input_file):
    """预处理输入图像"""
    image, _ = LoadImageFromPath(input_file)
    image, _, _, _, _ = SFImageScalerByPixels(image, 'lanczos', 2.0000000000000004, True, None)
    aligned_image, _, inverse_rotation_angle = SFAlignImageByFace(models['analysis_models'], image, True, False, None)
    bounding_infos, crop_images, _, = SFFaceCutout(models['analysis_models'], aligned_image, 0, 0.4000000000000001, 'sdxl', 1, 42, 0, 24, False)
    _, _, _, _, crop_image, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
    
    return {
        'original_image': image,
        'aligned_image': aligned_image,
        'crop_image': crop_image,
        'bounding_info': bounding_info,
        'inverse_rotation_angle': inverse_rotation_angle
    }


def setup_conditioning(clip):
    """设置正向和负向提示词"""
    conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,a beautiful girl, Look at the camera, Real photography, 4K, RAW photo, close-up, exquisite makeup, delicate skin,  real photos, best picture quality, high details', clip, 'length+mean', 'A1111')
    conditioning2 = SFAdvancedCLIPTextEncode('lowres, bad anatomy, bad hands, text, error, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet', clip, 'length+mean', 'A1111')
    
    return conditioning, conditioning2


def generate_face(models, image_data, model, vae, positive, negative):
    """生成人脸"""
    model2 = DifferentialDiffusion(model)
    
    # 第一次采样
    latent = VAEEncode(image_data['crop_image'], vae)
    latent = KSamplerAdvanced(model, True, 100006, 4, 1.4000000000000001, 'dpmpp_sde', 'karras', positive, negative, latent, 1, 2, False)
    image3 = VAEDecode(latent, vae)
    
    # 生成遮罩
    _, inverted_mask, _ = SFGeneratePreciseFaceMask(models['occluder'], image_data['crop_image'], 0.1, None)
    inverted_mask, _ = SFMaskChange(inverted_mask, 0, 0, False, 4, False)
    
    # 合成图像
    image4 = ImageCompositeMasked(image3, image_data['crop_image'], 0, 0, False, inverted_mask)
    
    # 边缘检测
    image5 = Canny(image4, 0.10000000000000002, 0.20000000000000004)
    
    # 应用ControlNet
    positive2, negative2 = ControlNetApplyAdvanced(positive, negative, models['control_net2'], image5, 0.8000000000000002, 0, 1, vae)
    
    # 第二次采样
    latent2 = VAEEncode(image_data['crop_image'], vae)
    mask_params = SFMaskParams(0, 0.07, False, 15, False)
    mask, _, _ = SFGeneratePreciseFaceMask(models['occluder'], image_data['crop_image'], 0.1, mask_params)
    latent2 = SetLatentNoiseMask(latent2, mask)
    latent2 = KSamplerAdvanced(model2, True, 100009, 7, 1.2, 'dpmpp_sde', 'karras', positive2, negative2, latent2, 3, 7, False)
    
    return VAEDecode(latent2, vae)


def postprocess_image(image, image_data, output_file):
    """后处理图像并保存"""
    image7 = SFImageColorMatch(image, image, 'LAB', 1, 'auto', 0, None)
    image8, _ = SFFacePaste(image_data['bounding_info'], image7, image_data['aligned_image'])
    image8 = SFImageRotate(image8, image_data['inverse_rotation_angle'], True)
    image8 = SFTrimImageBorders(image8, 10)
    
    # 保存图像
    images = util.get_images(image8)
    images[0].save(output_file) # type: ignore


def run_v2(char: str, input_file: str, output_file: str,  expression_edit: bool = False,
        message_callback=None):
    """
    换脸核心逻辑，仅处理单个文件
    
    Args:
        char: 人脸LoRA名称
        input_file: 输入文件路径
        output_file: 输出文件路径
        expression_edit: 是否编辑表情
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
            # 1. 加载模型
            models = load_models()
            
            # 2. 加载角色和基础模型
            model, clip, vae, char_image = load_character_and_base_models(char)
            
            # 3. 预处理图像
            image_data = preprocess_image(models, input_file)
            
            # 4. 设置条件提示词
            positive, negative = setup_conditioning(clip)
            
            # 5. 应用InstantID
            model, positive, negative = ApplyInstantIDAdvanced(
                models['instantid'], models['insightface_model'], models['control_net'], 
                char_image, model, positive, negative, 0, 0.6000000000000001, 
                0, 1, 0, 'average', image_data['crop_image'], None
            )
            
            # 6. 生成人脸
            face_image = generate_face(models, image_data, model, vae, positive, negative)
            
            # 7. 后处理并保存
            postprocess_image(face_image, image_data, output_file)
                        
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise 