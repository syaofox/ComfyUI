from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *




with Workflow():
    image, _ = LoadImage('mmexport1705073154703.jpg')
    masks = APersonMaskGenerator(image, False, False, False, False, True, 0.10000000000000002, True)
    masks, _ = MaskChange(masks, 32, 0, False, 5, False)
    masks2 = APersonMaskGenerator(image, False, False, False, True, False, 0.20000000000000004, True)
    masks2, _ = MaskChange(masks2, -20, 0, False, 5, False)
    mask = MaskComposite(masks, masks2, 0, 0, 'subtract')
    masks3 = APersonMaskGenerator(image, True, False, False, False, False, 0.20000000000000004, True)
    mask2 = MaskComposite(mask, masks3, 0, 0, 'subtract')
    stitcher, cropped_image, mask2 = InpaintCrop(image, 'bilinear', 'bicubic', False, 'sd15', 1, True, 0, False, 32, 0.1, False, 1, 1, 1, 1, 1.2, '32', True, 'custom', 0.5, mask2, None)
    model, clip, vae = CheckpointLoaderSimple(r'sd\majicmixRealistic_v7-inpainting.safetensors')
    clip = CLIPSetLastLayer(clip, -2)
    model, clip = LoraLoader(model, clip, r'sd15\good nipples.safetensors', 0.6000000000000001, 0.6000000000000001)
    model, clip = LoraLoader(model, clip, r'sd15\CutePussyVer2S.safetensors', 0.6000000000000001, 0.6000000000000001)
    conditioning = BNKCLIPTextEncodeAdvanced('slim asian girl,(completely nude:1.2),(tiny breasts:1.25), pussy,vagina,small breasts,small nipples,realistic, detailed', clip, 'length+mean', 'A1111')
    conditioning2 = BNKCLIPTextEncodeAdvanced('lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry', clip, 'length+mean', 'A1111')
    positive, negative, latent = InpaintModelConditioning(conditioning, conditioning2, vae, cropped_image, mask2, True)
    control_net = ControlNetLoader(r'sd15\control_v11p_sd15_openpose_fp16.safetensors')
    image3 = AIOPreprocessor(cropped_image, 'DWPreprocessor', 512)
    positive2, negative2 = ControlNetApplyAdvanced(positive, negative, control_net, image3, 0.8500000000000002, 0, 1, vae)
    image4 = cropped_image
    latent = KSampler(model, 11, 20, 3, 'dpmpp_sde', 'karras', positive2, negative2, latent, 1)
    image5 = VAEDecode(latent, vae)
    image5 = InpaintStitch(stitcher, image5)
    # PreviewImage(image5)
    SaveImage(image5, 'task')

    # images = util.get_images(image5)
    # for image in images:
    #     image.save(f'{image.filename}.png')
    # # `images` is of type `list[PIL.Image.Image]`