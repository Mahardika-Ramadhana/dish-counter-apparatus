import os
import cv2
import shutil
import glob

DATASET_DIR = "/home/dika/projects/dish-counter-apparatus/dataset"

# Move valid and test to train
for split in ['valid', 'test']:
    for folder in ['images', 'labels']:
        src_dir = os.path.join(DATASET_DIR, split, folder)
        dest_dir = os.path.join(DATASET_DIR, 'train', folder)
        if not os.path.exists(src_dir): continue
        os.makedirs(dest_dir, exist_ok=True)
        for f in glob.glob(os.path.join(src_dir, '*')):
            shutil.move(f, os.path.join(dest_dir, os.path.basename(f)))

train_img_dir = os.path.join(DATASET_DIR, 'train', 'images')
train_lbl_dir = os.path.join(DATASET_DIR, 'train', 'labels')

images = glob.glob(os.path.join(train_img_dir, '*.jpg'))
for img_path in images:
    if '_flip' in img_path or '_bright' in img_path or '_dark' in img_path:
        continue # Skip already augmented

    base_name = os.path.basename(img_path)
    name, ext = os.path.splitext(base_name)
    lbl_path = os.path.join(train_lbl_dir, name + '.txt')
    
    if not os.path.exists(lbl_path): continue
        
    img = cv2.imread(img_path)
    if img is None: continue

    with open(lbl_path, 'r') as f:
        lbl_data = f.read().strip().split('\n')
        
    # 1. Horizontal Flip
    flip_img = cv2.flip(img, 1)
    flip_lbl_data = []
    for line in lbl_data:
        parts = line.strip().split()
        if len(parts) < 3: continue
        cls = parts[0]
        coords = [float(p) for p in parts[1:]]
        # Flip X coords (which are at even indices in the 0-indexed coords list)
        for i in range(0, len(coords), 2):
            coords[i] = 1.0 - coords[i]
        flip_lbl_data.append(f"{cls} " + " ".join([f"{c:.6f}" for c in coords]))
        
    cv2.imwrite(os.path.join(train_img_dir, name + '_flip' + ext), flip_img)
    with open(os.path.join(train_lbl_dir, name + '_flip.txt'), 'w') as f:
        f.write('\n'.join(flip_lbl_data))

    # 2. Brightness
    bright_img = cv2.convertScaleAbs(img, alpha=1.2, beta=30)
    cv2.imwrite(os.path.join(train_img_dir, name + '_bright' + ext), bright_img)
    with open(os.path.join(train_lbl_dir, name + '_bright.txt'), 'w') as f:
        f.write('\n'.join(lbl_data))
        
    # 3. Darkness
    dark_img = cv2.convertScaleAbs(img, alpha=0.8, beta=-30)
    cv2.imwrite(os.path.join(train_img_dir, name + '_dark' + ext), dark_img)
    with open(os.path.join(train_lbl_dir, name + '_dark.txt'), 'w') as f:
        f.write('\n'.join(lbl_data))

print("Augmentation complete!")
