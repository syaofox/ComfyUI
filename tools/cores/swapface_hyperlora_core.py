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
            # insightface, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            # image, _ = LoadImageFromPath(input_file)
            # image, _, _, _, _ = SFImageScalerForSDModels(image, 'lanczos', 'sdxl', None)
            # aligned_image, rotation_info = SFAlignImageByFace(analysis_models, image, True, False, 10, False, None)
            # bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, aligned_image, 0, 0.5000000000000001, 'sdxl', 1, 0, 0.1, 32, False, False)
            # _, _, _, _, crop_image, _, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            # instantid = InstantIDModelLoader('ip-adapter.bin')
            # control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            # lora, image2 = HyperLoRALoadCharLoRA(char)
            # model, clip, vae = CheckpointLoaderSimple(r'xl\pornmaster_proSDXLV4VAE.safetensors')
            # model = HyperLoRAApplyLoRA(model, lora, 0.8)
            # conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,a beautiful girl,close up', clip, 'length+mean', 'A1111')
            # clip2 = CLIPSetLastLayer(clip, -2)
            # conditioning2 = SFAdvancedCLIPTextEncode('text, watermark,tatoo,extra leg,extra finger,extra hand,extra arms,extra legs', clip2, 'length+mean', 'A1111')
            # model, positive, negative = ApplyInstantIDAdvanced(instantid, insightface, control_net, image2, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', aligned_image, None)
            # control_net2 = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
            # control_net2 = SetUnionControlNetType(control_net2, 'tile')
            # image3 = AIOPreprocessor(crop_image, 'TilePreprocessor', 512)
            # positive2, negative2 = ACNAdvancedControlNetApplyV2(positive, negative, control_net2, image3, 0.45000000000000007, 0, 0.5000000000000001, None, None, None, None, vae)
            # sampler = KSamplerSelect('dpmpp_2m')
            # sigmas = AlignYourStepsScheduler('SDXL', 10, 0.7000000000000002)
            # latent = VAEEncode(crop_image, vae)
            # segmenter = SFPersonSegmenterLoader()
            # reshaped_image = SFFaceReshape(crop_image, 0.8500000000000002, 0.8500000000000002, '是', 'CPU')
            # masks = SFPersonMaskGenerator(segmenter, reshaped_image, True, False, False, False, False, 0.6000000000000001, True)
            # masks, _ = SFMaskChange(masks, 0, 0, False, 6, False)
            # latent = SetLatentNoiseMask(latent, masks)
            # latent, _ = SamplerCustom(model, True, 1002, 6, positive2, negative2, sampler, sigmas, latent)
            # image4 = VAEDecode(latent, vae)
            # image5 = SFImageColorMatch(image4, crop_image, 'LAB', 1, 'auto', 0, None)
            # image6, _ = SFFacePaste(bounding_info, image5, aligned_image)
            # image6 = SFRestoreRotatedImage(image6, rotation_info)  

            # insightface, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            # image, _ = LoadImageFromPath(input_file)
            # image, _, _, _, _ = SFImageScalerForSDModels(image, 'lanczos', 'sdxl', None)
            # aligned_image, rotation_info = SFAlignImageByFace(analysis_models, image, True, False, 10, False, None)
            # bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, aligned_image, 0, 0.5000000000000001, 'sdxl', 1, 0, 0.1, 32, False, False)
            # _, _, _, _, crop_image, _, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            # model, clip, vae = CheckpointLoaderSimple(r'xl\juggernautXL_ragnarokBy.safetensors')
            # lora, image2 = HyperLoRALoadCharLoRA(char)
            # model = HyperLoRAApplyLoRA(model, lora, 0.8)
            # clip = CLIPSetLastLayer(clip, -2)
            # conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,a beautiful girl,close up', clip, 'length+mean', 'A1111')
            # conditioning2 = SFAdvancedCLIPTextEncode('text, watermark,tatoo,extra leg,extra finger,extra hand,extra arms,extra legs', clip, 'length+mean', 'A1111')
            # sampler = KSamplerSelect('dpmpp_2m')
            # sigmas = AlignYourStepsScheduler('SDXL', 10, 0.25000000000000006)
            # instantid = InstantIDModelLoader('ip-adapter.bin')
            # control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            # model2, positive, negative = ApplyInstantIDAdvanced(instantid, insightface, control_net, image2, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', aligned_image, None)
            # control_net2 = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
            # control_net2 = SetUnionControlNetType(control_net2, 'repaint')
            # segmenter = SFPersonSegmenterLoader()
            # reshaped_image = SFFaceReshape(crop_image, 0.8000000000000002, 0.8000000000000002, '是', 'CPU')
            # masks = SFPersonMaskGenerator(segmenter, reshaped_image, True, False, False, False, False, 0.6000000000000001, True)
            # masks, _ = SFMaskChange(masks, 0, 0.010000000000000002, False, 6, True)
            # image3 = InpaintPreprocessor(crop_image, masks, True)
            # positive2, negative2 = ACNAdvancedControlNetApplyV2(positive, negative, control_net2, image3, 0.8500000000000002, 0, 1, None, None, None, None, vae)
            # sigmas2 = AlignYourStepsScheduler('SDXL', 10, 0.7000000000000002)
            # latent = VAEEncode(crop_image, vae)
            # latent, _ = SamplerCustom(model2, True, 1004, 4, positive2, negative2, sampler, sigmas2, latent)
            # image4 = VAEDecode(latent, vae)
            # image4 = ImageSharpen(image4, 1, 0.5000000000000001, 0.5000000000000001)
            # latent2 = VAEEncode(image4, vae)
            # latent2, _ = SamplerCustom(model, True, 1010, 4, conditioning, conditioning2, sampler, sigmas, latent2)
            # image5 = VAEDecode(latent2, vae)
            # image6 = SFImageColorMatch(image5, crop_image, 'LAB', 1, 'auto', 0, None)
            # image7, _ = SFFacePaste(bounding_info, image6, aligned_image)
            # image7 = SFRestoreRotatedImage(image7, rotation_info)

            # insightface, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            # image, _ = LoadImageFromPath(input_file)
            # image, _, _, _, _ = SFImageScalerForSDModels(image, 'lanczos', 'sdxl', None)
            # aligned_image, rotation_info = SFAlignImageByFace(analysis_models, image, True, False, 10, False, None)
            # bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, aligned_image, 0, 0.30000000000000004, 'sdxl', 1, 32, 0, 16, False, False)
            # x, y, width, height, crop_image, _, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            # instantid = InstantIDModelLoader('ip-adapter.bin')
            # control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            # lora, _, charname = HyperLoRALoadCharLoRA(char)
            # charname, _ = SFSelectFace(char, charname)
            # _, image_batch, _ = SFLoadImagesFromFolder(charname, 0, 4)
            # model, clip, vae = CheckpointLoaderSimple(r'xl\RealitiesEdgeXLLIGHTNING_TURBOV7.safetensors')
            # model = HyperLoRAApplyLoRA(model, lora, 0.8)
            # clip = CLIPSetLastLayer(clip, -2)
            # conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,Close up girl portrait, looking at the camera, smile,high quality, high detail', clip, 'length+mean', 'A1111')
            # conditioning2 = SFAdvancedCLIPTextEncode('text, watermark,tatoo,extra leg,extra finger,extra hand,extra arms,extra legs', clip, 'length+mean', 'A1111')
            # model2, positive, negative = ApplyInstantIDAdvanced(instantid, insightface, control_net, image_batch, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', crop_image, None)
            # sampler = KSamplerSelect('dpmpp_2m')
            # sigmas = AlignYourStepsScheduler('SDXL', 10, 0.5500000000000002)
            # conditioning3 = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks, a girl, looking at the camera, high quality, high detail', clip, 'length+mean', 'A1111')
            # image2, _, _, _, _ = SFImageScalerForSDModels(aligned_image, 'lanczos', 'sdxl', None)
            # model3, positive2, negative2 = ApplyInstantIDAdvanced(instantid, insightface, control_net, image_batch, model, conditioning3, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', image2, None)
            # sigmas2 = AlignYourStepsScheduler('SDXL', 4, 0.6500000000000001)
            # latent = VAEEncode(image2, vae)
            # latent, _ = SamplerCustom(model3, True, 0, 2, positive2, negative2, sampler, sigmas2, latent)
            # image3 = VAEDecode(latent, vae)
            # width2, height2, _, _, _ = SFGetImageSize(aligned_image)
            # image4 = ImageScale(image3, 'lanczos', width2, height2, 'disabled')
            # image4 = ImageCrop(image4, width, height, x, y)
            # warped_image = SFFaceMorph(crop_image, image4, 'OUTLINE', 'Width', 'CPU')
            # warped_image2 = SFFaceMorph(warped_image, image4, 'OUTLINE', 'Height', 'CPU')
            # warped_image3 = SFFaceMorph(warped_image2, image4, 'OUTLINE', 'JawLine', 'CPU')
            # latent2 = VAEEncode(warped_image3, vae)
            # segmenter = SFPersonSegmenterLoader()
            # masks = SFPersonMaskGenerator(segmenter, warped_image3, True, False, False, False, False, 0.6000000000000001, True)
            # masks, _ = SFMaskChange(masks, 8, 0, False, 6, False)
            # latent2 = SetLatentNoiseMask(latent2, masks)
            # latent2, _ = SamplerCustom(model2, True, 7, 2, positive, negative, sampler, sigmas, latent2)
            # image5 = VAEDecode(latent2, vae)
            # image6 = SFImageColorMatch(image5, crop_image, 'LAB', 1, 'auto', 0, None)
            # image7, mask = SFFacePaste(bounding_info, image6, aligned_image)
            # image7 = SFRestoreRotatedImage(image7, rotation_info)
            # ImageComparerRgthree(image7, image)          
            # postprocess_image(image7, output_file)

            insightface, analysis_models = SFFaceAnalysisModels('antelopev2', 'CUDA')
            image, _ = LoadImageFromPath(input_file)
            aligned_image, rotation_info = SFAlignImageByFace(analysis_models, image, True, False, 10, False, None)
            bounding_infos, crop_images, _ = SFFaceCutout(analysis_models, aligned_image, 0, 0.4000000000000001, 'sdxl', 1, 0, 0.1, 32, False, True)
            _, _, _, _, crop_image, _, bounding_info = SFExtractBoundingBox(bounding_infos, crop_images, 0)
            instantid = InstantIDModelLoader('ip-adapter.bin')
            control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
            lora, _, charname = HyperLoRALoadCharLoRA(char)
            charname, _ = SFSelectFace(char, charname)
            _, image_batch, _ = SFLoadImagesFromFolder(charname, 0, 2)
            model, clip, vae = CheckpointLoaderSimple(r'xl\juggernautXL_ragnarokBy.safetensors')
            model, clip = LoraLoader(model, clip, r'sdxl\m99_labiaplasty_pussy_2_sdxl.safetensors', 0.8000000000000002, 0.8000000000000002)
            model = HyperLoRAApplyLoRA(model, lora, 0.85)
            conditioning = SFAdvancedCLIPTextEncode('fcsks fxhks fhyks,A close-up portrait of a 20yo beautiful japanese girl', clip, 'length+mean', 'A1111')
            conditioning2 = SFAdvancedCLIPTextEncode('blurry, low quality, noisy, messy, illustration, text, watermark', clip, 'length+mean', 'A1111')
            model2, positive, negative = ApplyInstantIDAdvanced(instantid, insightface, control_net, image_batch, model, conditioning, conditioning2, 0, 0.6000000000000001, 0, 1, 0, 'average', crop_image, None)
            sampler = KSamplerSelect('dpmpp_sde')
            sigmas = AlignYourStepsScheduler('SDXL', 20, 0.3500000000000001)
            model3, ipadapter = IPAdapterUnifiedLoader(model, 'PLUS (high strength)', None)
            image2 = PrepImageForClipVision(crop_image, 'LANCZOS', 'center', 0)
            image3, _ = LoadImage('style (4).png')
            image3 = IPAdapterNoise('shuffle', 0.30000000000000004, 2, image3)
            model3 = IPAdapterStyleComposition(model3, ipadapter, image2, image2, 1.0000000000000002, 3.0000000000000004, False, 'average', 0, 0.8000000000000002, 'V only', image3, None, None)
            sigmas2 = AlignYourStepsScheduler('SDXL', 20, 0.45000000000000007)
            latent = VAEEncode(crop_image, vae)
            latent, _ = SamplerCustom(model3, True, 1004, 3, conditioning, conditioning2, sampler, sigmas2, latent)
            output, _ = SamplerCustom(model2, True, 10000, 3, positive, negative, sampler, sigmas, latent)
            image4 = VAEDecode(output, vae)
            image5 = SFImageColorMatch(image4, crop_image, 'RGB', 1, 'gpu', 0, None)
            image6, _ = SFFacePaste(bounding_info, image5, aligned_image)
            image6 = SFRestoreRotatedImage(image6, rotation_info)
            postprocess_image(image6, output_file)
                        
        if message_callback:
            message_callback(f'{os.path.basename(input_file)} 处理完成')
            
    except Exception as e:
        error_msg = f'{os.path.basename(input_file)} 处理失败: {e}'
        if message_callback:
            message_callback(error_msg)
        # 抛出异常，让上层处理
        raise