import PIL.Image
import os
import argparse
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

from tqdm import tqdm


def run(input_path:str, output_path:str):
    queue.watch_display(False)
   
    with Workflow(input_path, output_path):

        image,_ = LoadImageFromPath(input_path)
        
        masks = APersonMaskGenerator(image, False, False, False, False, True, 0.10000000000000002, True)
        masks, _ = MaskChange(masks, 20, 0, False, 5, False)
        masks2 = APersonMaskGenerator(image, False, False, False, True, False, 0.20000000000000004, True)
        masks2, _ = MaskChange(masks2, -5, 0, False, 5, False)
        mask = MaskComposite(masks, masks2, 0, 0, 'subtract')
        masks3 = APersonMaskGenerator(image, True, False, False, False, False, 0.20000000000000004, True)
        mask2 = MaskComposite(mask, masks3, 0, 0, 'subtract')
        stitcher, cropped_image, cropped_mask = InpaintCrop(image, 'bilinear', 'bicubic', False, 'sd15', 1, True, 0, False, 32, 0.1, False, 1, 1, 1, 1, 1.2, '32', True, 'sdxl', 0.5, mask2, None)
        model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
        clip = CLIPSetLastLayer(clip, -2)
        model, clip = LoraLoader(model, clip, r'sdxl\m99_labiaplasty_pussy_2_sdxl.safetensors', 0.6000000000000001, 1.0000000000000002)
        conditioning = BNKCLIPTextEncodeAdvanced('slim asian girl,(completely nude:1.2),(tiny breasts:1.25), pussy,vagina,small breasts,small nipples,(no pubic hair , vaginal lips clearly visible:1.2),realistic, detailed', clip, 'length+mean', 'A1111')
        conditioning2 = BNKCLIPTextEncodeAdvanced('lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry', clip, 'length+mean', 'A1111')
        control_net = ControlNetLoader(r'xinsir\controlnet-union-sdxl-1.0_promax.safetensors')
        control_net2 = SetUnionControlNetType(control_net, 'openpose')
        image3 = AIOPreprocessor(cropped_image, 'DWPreprocessor', 512)
        positive, negative = ControlNetApplyAdvanced(conditioning, conditioning2, control_net2, image3, 0.8000000000000002, 0, 1, vae)
        control_net3 = SetUnionControlNetType(control_net, 'repaint')
        image4 = InpaintPreprocessor(cropped_image, cropped_mask, True)
        positive2, negative2 = ControlNetApplyAdvanced(positive, negative, control_net3, image4, 0.7800000000000001, 0, 1, vae)
        latent = VAEEncode(cropped_image, vae)
        latent = KSampler(model, 13, 4, 1.2, 'dpmpp_sde', 'karras', positive2, negative2, latent, 1)
        image5 = VAEDecode(latent, vae)
        image5 = InpaintStitch(stitcher, image5)

        images:list[PIL.Image.Image] = util.get_images(image5)
        
        images[0].save(output_path)



def main():
    args = argparse.ArgumentParser()
    # 使用位置参数而不是选项参数
    args.add_argument('input_path', type=str, help='输入路径')
    args.add_argument('output_path', type=str, help='输出路径')
    args = args.parse_args()

    # 从文件夹读取所有图片
    input_path = args.input_path
    output_path = args.output_path

    os.makedirs(output_path, exist_ok=True)
    for file in tqdm(os.listdir(input_path),desc='总进度'):
        if file.lower().endswith('.jpg') or file.lower().endswith('.png') or file.lower().endswith('.jpeg') or file.lower().endswith('.webp'):
            # 如果目标文件存在，则跳过
            if os.path.exists(os.path.join(output_path, file)):
                continue
            run(os.path.join(input_path, file), os.path.join(output_path, file))




if __name__ == '__main__':
    main()
