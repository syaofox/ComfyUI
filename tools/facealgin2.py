import argparse
import glob
import os
from pathlib import Path

import cv2
import numpy as np
import PIL
import PIL.Image
import scipy
import scipy.ndimage
from dlib import get_frontal_face_detector, shape_predictor  # type: ignore

# 模型路径
model_path = str(Path(__file__).parent.parent / "models" / "dlib" / "shape_predictor_68_face_landmarks.dat")
predictor = shape_predictor(model_path)


def get_landmark(filepath, only_keep_largest=True):
    detector = get_frontal_face_detector()

    img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), cv2.IMREAD_COLOR)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    dets = detector(img, 1)

    print("\tNumber of faces detected: {}".format(len(dets)))

    for k, d in enumerate(dets):
        shape = predictor(img, d)

        t = list(shape.parts())
        a = []
        for tt in t:
            a.append([tt.x, tt.y])
        lm = np.array(a)

        yield lm


def align_face(
    filepath,
    out_path,
    expand_top: float = 0.0,
    expand_right: float = 0.0,
    expand_bottom: float = 0.0,
    expand_left: float = 0.0,
    short_side: int | None = 1200,
):
    """
    :param filepath: str
    :param out_path: str
    :param expand_top: float 比例，基于初始人脸检测到的裁切高（0~1通常），向上额外扩展比例
    :param expand_right: float 比例，基于初始人脸检测到的裁切宽，向右额外扩展比例
    :param expand_bottom: float 比例，基于初始人脸检测到的裁切高，向下额外扩展比例
    :param expand_left: float 比例，基于初始人脸检测到的裁切宽，向左额外扩展比例
    :param short_side: 最终输出短边目标像素，保持长宽比缩放；传入 None 或 <=0 表示不缩放
    :return: PIL Image
    """

    try:
        lme = get_landmark(filepath, only_keep_largest=False)
    except Exception as e:
        print("No landmark ...")
        return

    for idx, lm in enumerate(lme):
        lm_eye_left = lm[36:42]  # left-clockwise
        lm_eye_right = lm[42:48]  # left-clockwise
        lm_mouth_outer = lm[48:60]  # left-clockwise

        # Calculate auxiliary vectors.
        eye_left = np.mean(lm_eye_left, axis=0)
        eye_right = np.mean(lm_eye_right, axis=0)
        eye_avg = (eye_left + eye_right) * 0.5
        eye_to_eye = eye_right - eye_left
        mouth_left = lm_mouth_outer[0]
        mouth_right = lm_mouth_outer[6]
        mouth_avg = (mouth_left + mouth_right) * 0.5
        eye_to_mouth = mouth_avg - eye_avg

        # Choose oriented crop rectangle.
        x = eye_to_eye - np.flipud(eye_to_mouth) * [-1, 1]
        x /= np.hypot(*x)
        x *= max(np.hypot(*eye_to_eye) * 2.0, np.hypot(*eye_to_mouth) * 1.8)
        y = np.flipud(x) * [-1, 1]
        c = eye_avg + eye_to_mouth * 0.1
        quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])

        # 基于用户的四向扩展比例，直接对 quad 四个角做定向外扩
        # 计算沿 x/y 方向的单位向量与长度
        lx = float(np.hypot(*x))
        ly = float(np.hypot(*y))
        if lx > 0 and ly > 0:
            ux = x / lx
            uy = y / ly
            # 各方向位移量（以当前半边长度为尺度）
            delta_right = ux * (expand_right * lx)
            delta_left = -ux * (expand_left * lx)
            delta_bottom = uy * (expand_bottom * ly)
            delta_top = -uy * (expand_top * ly)
            # 顶边角: idx 0(-x,-y), idx 3(+x,-y)
            quad[0] = quad[0] + delta_left + delta_top
            quad[3] = quad[3] + delta_right + delta_top
            # 底边角: idx 1(-x,+y), idx 2(+x,+y)
            quad[1] = quad[1] + delta_left + delta_bottom
            quad[2] = quad[2] + delta_right + delta_bottom

        # 基于更新后的四边形重新估算 qsize（用于后续 shrink/border 计算）
        e01 = np.linalg.norm(quad[1] - quad[0])
        e12 = np.linalg.norm(quad[2] - quad[1])
        e23 = np.linalg.norm(quad[3] - quad[2])
        e30 = np.linalg.norm(quad[0] - quad[3])
        qsize = max(e01, e12, e23, e30)

        # read image
        img = PIL.Image.open(filepath)

        enable_padding = False

        # 基于四边形边长估计输出宽高（不固定、不缩放）
        w_top = float(np.linalg.norm(quad[3] - quad[0]))
        w_bottom = float(np.linalg.norm(quad[2] - quad[1]))
        h_left = float(np.linalg.norm(quad[1] - quad[0]))
        h_right = float(np.linalg.norm(quad[2] - quad[3]))
        width = max(1, int(np.rint((w_top + w_bottom) * 0.5)))
        height = max(1, int(np.rint((h_left + h_right) * 0.5)))
        qsize = float(max(width, height))

        # Crop.
        border = max(int(np.rint(qsize * 0.05)), 3)
        # 基于四点得到初始包围盒（未加边框）
        crop_raw = (
            int(np.floor(min(quad[:, 0]))),
            int(np.floor(min(quad[:, 1]))),
            int(np.ceil(max(quad[:, 0]))),
            int(np.ceil(max(quad[:, 1]))),
        )
        crop_w = crop_raw[2] - crop_raw[0]
        crop_h = crop_raw[3] - crop_raw[1]
        # 先按 border 扩展，再按用户定义的四向比例扩展（以初始宽高为基准）
        crop_pre = (
            crop_raw[0] - border - int(np.rint(expand_left * crop_w)),
            crop_raw[1] - border - int(np.rint(expand_top * crop_h)),
            crop_raw[2] + border + int(np.rint(expand_right * crop_w)),
            crop_raw[3] + border + int(np.rint(expand_bottom * crop_h)),
        )
        # 再进行与图像边界的裁切限制
        crop = (
            max(crop_pre[0], 0),
            max(crop_pre[1], 0),
            min(crop_pre[2], img.size[0]),
            min(crop_pre[3], img.size[1]),
        )
        if crop[2] - crop[0] < img.size[0] or crop[3] - crop[1] < img.size[1]:
            img = img.crop(crop)
            quad -= crop[0:2]

        # Pad.
        pad = (
            int(np.floor(min(quad[:, 0]))),
            int(np.floor(min(quad[:, 1]))),
            int(np.ceil(max(quad[:, 0]))),
            int(np.ceil(max(quad[:, 1]))),
        )
        pad = (
            max(-pad[0] + border, 0),
            max(-pad[1] + border, 0),
            max(pad[2] - img.size[0] + border, 0),
            max(pad[3] - img.size[1] + border, 0),
        )
        if enable_padding and max(pad) > border - 4:
            pad = np.maximum(pad, int(np.rint(qsize * 0.3)))
            img = np.pad(  # type: ignore
                np.float32(img),  # type: ignore
                ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)),
                "reflect",
            )
            h, w, _ = img.shape
            y, x, _ = np.ogrid[:h, :w, :1]
            mask = np.maximum(
                1.0
                - np.minimum(np.float32(x) / pad[0], np.float32(w - 1 - x) / pad[2]),
                1.0
                - np.minimum(np.float32(y) / pad[1], np.float32(h - 1 - y) / pad[3]),
            )
            blur = qsize * 0.02
            img += (
                scipy.ndimage.gaussian_filter(img, [blur, blur, 0]) - img
            ) * np.clip(mask * 3.0 + 1.0, 0.0, 1.0)
            img += (np.median(img, axis=(0, 1)) - img) * np.clip(mask, 0.0, 1.0)
            img = PIL.Image.fromarray(np.uint8(np.clip(np.rint(img), 0, 255)), "RGB")
            quad += pad[:2]

        img = img.transform(
            (width, height),
            PIL.Image.Transform.QUAD,
            tuple((quad + 0.5).flatten().tolist()),
            PIL.Image.Resampling.BICUBIC,
        )

        # 若指定短边缩放，则按比例缩放到目标短边（不改变长宽比）
        if short_side is not None and int(short_side) > 0:
            cur_w, cur_h = img.size
            short = min(cur_w, cur_h)
            if short > 0 and short != short_side:
                scale = float(short_side) / float(short)
                new_w = max(1, int(np.rint(cur_w * scale)))
                new_h = max(1, int(np.rint(cur_h * scale)))
                if (new_w, new_h) != (cur_w, cur_h):
                    img = img.resize((new_w, new_h), PIL.Image.Resampling.LANCZOS)

        out_path = Path(out_path)
        nfname = f"{out_path.stem}_{idx:04}.png"
        ofname = out_path.parent / nfname
        img.save(ofname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="人脸对齐和裁剪")
    parser.add_argument("in_dir", type=str, help="输入图片目录路径")
    # parser.add_argument("out_dir", type=str, help="输出图片目录路径")
    parser.add_argument("--expand-top", dest="expand_top", type=float, default=0.5, help="向上扩展比例（基于初始裁切高）")
    parser.add_argument("--expand-right", dest="expand_right", type=float, default=0.7, help="向右扩展比例（基于初始裁切宽）")
    parser.add_argument("--expand-bottom", dest="expand_bottom", type=float, default=2.0, help="向下扩展比例（基于初始裁切高）")
    parser.add_argument("--expand-left", dest="expand_left", type=float, default=0.7, help="向左扩展比例（基于初始裁切宽）")
    parser.add_argument("--short-side", dest="short_side", type=int, default=1200, help="最终短边像素，保持长宽比缩放；<=0 代表不缩放")
    args = parser.parse_args()

    in_dir = args.in_dir
    # out_dir = args.out_dir


    out_dir = os.path.join(r'D:\codes\aivision\asserts\face_pieces',in_dir.split('\\')[-1])
    print(out_dir)

    os.makedirs(out_dir, exist_ok=True)

    img_list = sorted(glob.glob(os.path.join(in_dir, "*.[jpJP][pnPN]*[gG]")))
    test_img_num = len(img_list)

    for i, in_path in enumerate(img_list):
        img_name = os.path.basename(in_path)
        print(f"[{i+1}/{test_img_num}] Processing: {img_name}")

        out_path = Path(out_dir) / f"{Path(in_path).stem}.png"
        out_path = str(out_path)

        align_face(
            in_path,
            out_path,
            expand_top=args.expand_top,
            expand_right=args.expand_right,
            expand_bottom=args.expand_bottom,
            expand_left=args.expand_left,
            short_side=args.short_side,
        )
