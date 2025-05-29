import PIL.Image
import os
import argparse
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

from tqdm import tqdm

def run(char:str, input_path:str, output_path:str, repaint_hair:bool = True):
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
        image2, _ = LoadImageFromPath(input_path)
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


        try:    
            images:list[PIL.Image.Image] = util.get_images(image5)
            images[0].save(output_path)

        except AssertionError as e:
            print(e)
            print(f'{input_path} 处理失败')
            
        
        


def main():
    args = argparse.ArgumentParser()
    # 使用位置参数而不是选项参数
    args.add_argument('char', type=str, help='人脸')
    args.add_argument('input_path', type=str, help='输入路径')
    args.add_argument('output_path', type=str, help='输出路径')
    args.add_argument('--repaint_hair', type=bool, default=True, help='是否重绘头发，默认为True')
    
    args = args.parse_args()

    # 从文件夹读取所有图片
    input_path = args.input_path
    output_path = args.output_path

    os.makedirs(output_path, exist_ok=True)
    for file in tqdm(os.listdir(input_path),desc='总进度'):
        if file.lower().endswith('.jpg') or file.lower().endswith('.png') or file.lower().endswith('.jpeg') or file.lower().endswith('.webp'):
            # 如果目标文件存在，则跳过 
            if os.path.exists(os.path.join(output_path, file)):
                print(f'{file} 已存在,跳过')
                continue
            run(args.char, os.path.join(input_path, file), os.path.join(output_path, file), args.repaint_hair)

if __name__ == '__main__':
    main()
