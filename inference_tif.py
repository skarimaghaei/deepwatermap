import argparse
import deepwatermap
import tifffile as tiff
import numpy as np
import cv2

def find_padding(v, divisor=32):
    v_divisible = max(divisor, int(divisor * np.ceil( v / divisor )))
    total_pad = v_divisible - v
    pad_1 = total_pad // 2
    pad_2 = total_pad - pad_1
    return pad_1, pad_2

def main(checkpoint_path, image_path, save_path):
    # load the model
    model = deepwatermap.model()
    model.load_weights(checkpoint_path)

    # load and preprocess the input image
    image = tiff.imread(image_path)
    pad_r = find_padding(image.shape[0])
    pad_c = find_padding(image.shape[1])
    image = np.pad(image, ((pad_r[0], pad_r[1]), (pad_c[0], pad_c[1]), (0, 0)), 'reflect')

    # solve no-pad index issue after inference
    if pad_r[1] == 0:
        pad_r = (pad_r[0], 1)
    if pad_c[1] == 0:
        pad_c = (pad_c[0], 1)

    image = image.astype(np.float32)

    # remove nans (and infinity) - replace with 0s
    image = np.nan_to_num(image, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    
    image = image - np.min(image)
    image = image / np.maximum(np.max(image), 1)

    # run inference
    image = np.expand_dims(image, axis=0)
    dwm = model.predict(image)
    dwm = np.squeeze(dwm)
    dwm = dwm[pad_r[0]:-pad_r[1], pad_c[0]:-pad_c[1]]

    # soft threshold
    # dwm = 1./(1+np.exp(-(16*(dwm-0.5))))
    # dwm = np.clip(dwm, 0, 1)

    # making image purely binary
    # dwm = (dwm > 0.9).astype(np.float32)

    # making image purely binary using Otsu's method
    # Making image purely binary using Otsu's method
    dwm_scaled = (dwm * 255).astype(np.uint8)  # Scale to 8-bit for Otsu's method
    otsu_threshold, _ = cv2.threshold(dwm_scaled, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Correct order
    dwm = (dwm_scaled > otsu_threshold).astype(np.float32)
    print(f"Otsu Threshold: {otsu_threshold}")

    # save the output water map as a TIFF file
    tiff.imwrite(save_path, dwm.astype(np.float32))
    
    return dwm_scaled, otsu_threshold

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint_path', type=str,
                        help="Path to the dir where the checkpoints are stored")
    parser.add_argument('--image_path', type=str, help="Path to the input GeoTIFF image")
    parser.add_argument('--save_path', type=str, help="Path where the output map will be saved")
    args = parser.parse_args()
    main(args.checkpoint_path, args.image_path, args.save_path)
