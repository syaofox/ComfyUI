import PIL.Image
import os
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

def run_v1(char: str, input_file: str, output_file: str, sub_body: bool = True, expression_edit: bool = False,
        message_callback=None):
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
            analysis_models = SFFaceAnalysisModels('insightface', 'CUDA')
            image, _ = LoadImageFromPath(input_file)
            image, _, _, _, _ = SFImageScalerByPixels(image, 'lanczos', 2.8000000000000007, True, None)
            image, _, inverse_rotation_angle = SFAlignImageByFace(analysis_models, image, True, False, None)
            bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, image, 0, 0.4000000000000001, 'sdxl', 1, 12, 0, 10, True)
            _, _, _, _, crop_image, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            instantid = InstantIDModelLoader('ip-adapter.bin')
            faceanalysis = InstantIDFaceAnalysis('CUDA')
            control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            lora, image2 = HyperLoRALoadCharLoRA(char)
            model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
            model = HyperLoRAApplyLoRA(model, lora, 0.85)
            clip2 = CLIPSetLastLayer(clip, -1)
            conditioning = BNKCLIPTextEncodeAdvanced('fcsks fxhks fhyks,a beautiful girl, Look at the camera, Real photography, 4K, RAW photo, close-up, exquisite makeup, delicate skin,  real photos, best picture quality, high details', clip2, 'length+mean', 'A1111')
            conditioning2 = BNKCLIPTextEncodeAdvanced('finger,hande,lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet', clip2, 'length+mean', 'A1111')
            model, positive, negative = ApplyInstantIDAdvanced(instantid, faceanalysis, control_net, image2, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', crop_image, None)
            latent = VAEEncode(crop_image, vae)
            latent = KSamplerAdvanced(model, True, 100006, 4, 1.4000000000000001, 'dpmpp_sde', 'karras', positive, negative, latent, 1, 2, False)
            image3 = VAEDecode(latent, vae)
            warped_image = SFFaceMorph(crop_image, image3, 'OUTLINE', 'Landmarks', 'CPU')
            latent2 = VAEEncode(warped_image, vae)
            segmenter = SFPersonSegmenterLoader()
            if sub_body:
                
                occluder = SFOccluderLoader('xseg_3')
                mask, _, _ = SFGeneratePreciseFaceMask(occluder, warped_image, 0.1, 0, 0, False, 0, False)
                mask, _ = SFMaskChange(mask, -2, 0, False, 2, False)
                segmenter = SFPersonSegmenterLoader()
                masks = SFPersonMaskGenerator(segmenter, warped_image, False, False, False, True, False, 0.10000000000000002, True)
                mask = MaskComposite(mask, masks, 0, 0, 'subtract')
                steps = [7,3]
                print('去除身体, steps:', steps)

            else:       
                
                segmenter = SFPersonSegmenterLoader()
                mask = SFPersonMaskGenerator(segmenter, warped_image, True, False, True, False, False, 0.10000000000000002, True)
                steps = [8,4]
                print('不去除身体, steps:', steps)
                

            latent2 = SetLatentNoiseMask(latent2, mask)
            latent2 = KSamplerAdvanced(model, True, 100008, steps[0], 1.2, 'dpmpp_sde', 'karras', positive, negative, latent2, steps[1], steps[0], False)
            image4 = VAEDecode(latent2, vae)
            image5 = SFImageColorMatch(image4, image4, 'RGB', 1, 'auto', 0, None)

            if expression_edit:
                image6, _, _ = ExpressionEditor(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0.5000000000000001, 'OnlyExpression', 1.7, image5, None, crop_image, None)
                print('表情编辑')
            else:
                image6 = image5

            image6, _ = SFFacePaste(bounding_info, image5, image)
            image6 = SFImageRotate(image6, inverse_rotation_angle, True) # type: ignore
            image6 = SFTrimImageBorders(image6, 10) # type: ignore
            images = util.get_images(image6)  # type: ignore
            images[0].save(output_file) # type: ignore



                        
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise 



def run_v2(char: str, input_file: str, output_file: str, sub_body: bool = True, expression_edit: bool = False,
        message_callback=None):
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
            analysis_models = SFFaceAnalysisModels('insightface', 'CUDA')
            image, _ = LoadImageFromPath(input_file)
            image, _, _, _, _ = SFImageScalerByPixels(image, 'lanczos', 2.8000000000000007, True, None)
            image, _, inverse_rotation_angle = SFAlignImageByFace(analysis_models, image, True, False, None)
            bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, image, 0, 0.4000000000000001, 'sdxl', 1, 12, 0, 10, False)
            _, _, _, _, crop_image, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            instantid = InstantIDModelLoader('ip-adapter.bin')
            faceanalysis = InstantIDFaceAnalysis('CUDA')
            control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            lora, image2 = HyperLoRALoadCharLoRA(char)
            model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
            model = HyperLoRAApplyLoRA(model, lora, 0.85)
            clip2 = CLIPSetLastLayer(clip, -2)
            conditioning = BNKCLIPTextEncodeAdvanced('fcsks fxhks fhyks,a beautiful girl, Look at the camera, Real photography, 4K, RAW photo, close-up, exquisite makeup, delicate skin,  real photos, best picture quality, high details', clip2, 'length+mean', 'A1111')
            conditioning2 = BNKCLIPTextEncodeAdvanced('finger,hande,lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet', clip2, 'length+mean', 'A1111')
            model, positive, negative = ApplyInstantIDAdvanced(instantid, faceanalysis, control_net, image2, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', crop_image, None)
            model2 = DifferentialDiffusion(model)
            analysis_models2 = SFFaceAnalysisModels('insightface', 'CUDA')
            latent = VAEEncode(crop_image, vae)
            latent = KSamplerAdvanced(model, True, 100007, 4, 1, 'dpmpp_sde', 'karras', positive, negative, latent, 1, 4, False)
            image3 = VAEDecode(latent, vae)
            warped_image = SFFaceMorph(crop_image, image3, 'OUTLINE', 'Landmarks', 'CPU')
            occluder = SFOccluderLoader('xseg_3')
            mask_params = SFMaskParams(42, 0, False, 32, False)
            mask, _, _ = SFGeneratePreciseFaceMask(occluder, image3, 0.1, mask_params)
            mask2, _, _ = SFGeneratePreciseFaceMask(occluder, warped_image, 0.1, mask_params)
            image4, mask3 = SFFaceWarp(analysis_models2, image3, warped_image, 'full face', mask, mask2, mask_params)
            mask_params2 = SFMaskParams(-10, 0, False, 6, False)
            _, inverted_mask, _ = SFGeneratePreciseFaceMask(occluder, warped_image, 0.1, mask_params2)
            image5 = ImageCompositeMasked(image4, warped_image, 0, 0, False, inverted_mask)
            latent2 = VAEEncode(image5, vae)
            latent2 = SetLatentNoiseMask(latent2, mask3)
            latent2 = KSamplerAdvanced(model2, True, 100014, 9, 1, 'dpmpp_sde', 'karras', positive, negative, latent2, 5, 9, False)
            image6 = VAEDecode(latent2, vae)
            image7 = SFImageColorMatch(image6, crop_image, 'LAB', 1, 'auto', 0, None)
            image8, _ = SFFacePaste(bounding_info, image7, image)
            image8 = SFImageRotate(image8, inverse_rotation_angle, True) # type: ignore
            image8 = SFTrimImageBorders(image8, 10) # type: ignore
            images = util.get_images(image8)  # type: ignore
            images[0].save(output_file) # type: ignore



                        
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise 