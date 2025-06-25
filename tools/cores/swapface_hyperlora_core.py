import os
from comfy_script.runtime import * # type: ignore
load()
from comfy_script.runtime.nodes import * # type: ignore


def postprocess_image(image, output_file):

    images = util.get_images(image)
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
            insightface, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            image, _ = LoadImageFromPath(input_file)
            image, _, _, _, _ = SFImageScalerForSDModels(image, 'lanczos', 'sdxl', None)
            aligned_image, rotation_info = SFAlignImageByFace(analysis_models, image, True, False, 10, False, None)
            bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, aligned_image, 0, 0.5000000000000001, 'sdxl', 1, 0, 0.1, 32, False, False)
            _, _, _, _, crop_image, _, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            instantid = InstantIDModelLoader('ip-adapter.bin')
            control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            lora, image2 = HyperLoRALoadCharLoRA(char)
            model, clip, vae = CheckpointLoaderSimple(r'xl\pornmaster_proSDXLV4VAE.safetensors')
            model = HyperLoRAApplyLoRA(model, lora, 0.8)
            conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,a beautiful girl,close up', clip, 'length+mean', 'A1111')
            clip2 = CLIPSetLastLayer(clip, -2)
            conditioning2 = SFAdvancedCLIPTextEncode('text, watermark,tatoo,extra leg,extra finger,extra hand,extra arms,extra legs', clip2, 'length+mean', 'A1111')
            model, positive, negative = ApplyInstantIDAdvanced(instantid, insightface, control_net, image2, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', aligned_image, None)
            control_net2 = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
            control_net2 = SetUnionControlNetType(control_net2, 'tile')
            image3 = AIOPreprocessor(crop_image, 'TilePreprocessor', 512)
            positive2, negative2 = ACNAdvancedControlNetApplyV2(positive, negative, control_net2, image3, 0.45000000000000007, 0, 0.5000000000000001, None, None, None, None, vae)
            sampler = KSamplerSelect('dpmpp_2m')
            sigmas = AlignYourStepsScheduler('SDXL', 10, 0.7000000000000002)
            latent = VAEEncode(crop_image, vae)
            segmenter = SFPersonSegmenterLoader()
            reshaped_image = SFFaceReshape(crop_image, 0.8500000000000002, 0.8500000000000002, '是', 'CPU')
            masks = SFPersonMaskGenerator(segmenter, reshaped_image, True, False, False, False, False, 0.6000000000000001, True)
            masks, _ = SFMaskChange(masks, 0, 0, False, 6, False)
            latent = SetLatentNoiseMask(latent, masks)
            latent, _ = SamplerCustom(model, True, 1002, 6, positive2, negative2, sampler, sigmas, latent)
            image4 = VAEDecode(latent, vae)
            image5 = SFImageColorMatch(image4, crop_image, 'LAB', 1, 'auto', 0, None)
            image6, _ = SFFacePaste(bounding_info, image5, aligned_image)
            postprocess_image(image6, output_file)
                        
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise