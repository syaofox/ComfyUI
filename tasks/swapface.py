import PIL.Image
import os
import argparse
from comfy_script.runtime import *
load()
from comfy_script.runtime.nodes import *

from tqdm import tqdm

def run(char:str, input_path:str, output_path:str):
    queue.watch_display(False)
   
    with Workflow():
        instantid = InstantIDModelLoader('ip-adapter.bin')
        pulid = EcomIDPulidModelLoader('ip-adapter_pulid_sdxl_fp16.safetensors')
        eva_clip = PulidEvaClipLoader()
        faceanalysis = EcomIDFaceAnalysis('CPU')
        control_net = ControlNetLoader(r'instantid\diffusion_pytorch_model.safetensors')
        face_path, _ = SelectFace(char)
        _, image_batch, _ = LoadImagesFromFolder(face_path, 0, 1)
        occluder = OccluderLoader('xseg_3')
        rgba_image = image_batch
        model, clip, vae = CheckpointLoaderSimple(r'xl\dreamshaperXL_v21TurboDPMSDE.safetensors')
        clip2 = CLIPSetLastLayer(clip, -2)
        conditioning = BNKCLIPTextEncodeAdvanced('a beautiful girl,  Real photography, 4K, RAW photo, close-up, exquisite makeup, delicate skin,  real photos, best picture quality, high details', clip2, 'length+mean', 'A1111')
        conditioning2 = BNKCLIPTextEncodeAdvanced('finger,hande,lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, bad feet', clip2, 'length+mean', 'A1111')
        analysis_models = FaceAnalysisModels('insightface', 'CUDA')


        image, _ = LoadImageFromPath(input_path)
        image, _, _, _, _ = ImageScalerByPixels(image, 'lanczos', 2.8000000000000007, True, None)
        image, _, inverse_rotation_angle = AlignImageByFace(analysis_models, image, True, False, None)
        image, bounding_info = FaceCutout(analysis_models, image, 0, 0.5000000000000001, -1, 'sdxl', 1)
        model2, positive, negative = ApplyEcomIDAdvanced(instantid, pulid, eva_clip, faceanalysis, control_net, rgba_image, model, conditioning, conditioning2, 'fidelity', 0, 1, 0.8000000000000002, 0.8, 0, 'average', image, None)
        latent = VAEEncode(image, vae)
        latent = KSamplerAdvanced(model2, 'enable', 100006, 4, 1, 'dpmpp_sde', 'karras', positive, negative, latent, 1, 2, 'disable')
        image2 = VAEDecode(latent, vae)
        warped_image = FaceMorph(image, image2, 'OUTLINE', 'Landmarks', 'CPU')
        latent2 = VAEEncode(warped_image, vae)
        mask2, _, _ = GeneratePreciseFaceMask(occluder, warped_image, 0.1, 'none', 0, 0, False, 0, False)
        latent2 = SetLatentNoiseMask(latent2, mask2)
        latent2 = KSamplerAdvanced(model2, 'enable', 100007, 8, 1, 'dpmpp_sde', 'karras', positive, negative, latent2, 4, 8, 'disable')
        image3 = VAEDecode(latent2, vae)
        image4 = ImageColorMatch(image3, image3, 'RGB', 1, 'auto', 0, None)
        image4, _ = FacePaste(image4, bounding_info, 0, 0.05000000000000001, 20)
        image4 = ImageRotate(image4, inverse_rotation_angle, True)
        image4 = TrimImageBorders(image4, 10)

        images:list[PIL.Image.Image] = util.get_images(image4)
        
        images[0].save(output_path)



def main():
    args = argparse.ArgumentParser()
    # 使用位置参数而不是选项参数
    args.add_argument('char', type=str, help='人脸')
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
                print(f'{file} 已存在,跳过')
                continue
            run(args.char, os.path.join(input_path, file), os.path.join(output_path, file))

if __name__ == '__main__':
    main()
