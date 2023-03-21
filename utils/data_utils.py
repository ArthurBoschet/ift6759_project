import os
import numpy as np
import nibabel as nib

from tqdm import tqdm


def split_images_and_labels(input_folder):
    '''
    Split the images and labels from .npz files into separate .npy (numpy) files
    
    Args:
        input_folder: str 
            Path to the folder containing the images and labels
    '''
    image_dir = os.path.join(input_folder, 'imagesTr')
    label_dir = os.path.join(input_folder, 'labelsTr')
    for file in tqdm(os.listdir(image_dir)):
        if file.endswith('.npz'):
            data = np.load(os.path.join(image_dir, file))['data']
            idx = file.find('_')+1
            np.save(os.path.join(image_dir, f'image_{file[idx:idx+3]}.npy'), data[0])
            np.save(os.path.join(label_dir, f'label_{file[idx:idx+3]}.npy'), data[1])
            os.remove(os.path.join(image_dir, file))

def convert_niigz_to_numpy(input_folder):
    '''
    Convert the images and labels from .nii.gz files into .npy (numpy) files
    
    Args:
        input_folder: str
            Path to the folder containing the images and labels
    '''
    for subdir in ['imagesTr', 'labelsTr', 'imagesTs']:
        dir = os.path.join(input_folder, subdir)
        if os.path.exists(dir):
            for file in tqdm(os.listdir(dir)):
                if file.endswith('.nii.gz'):
                    data = nib.load(os.path.join(dir, file)).get_fdata()
                    data = np.transpose(data, (2, 0, 1))
                    idx = file.find('_')+1
                    np.save(os.path.join(dir, f'{subdir[:-3]}_{file[idx:idx+3]}.npy'), data)
                    os.remove(os.path.join(dir, file))

def convert_to_numpy(input_folder):
    '''
    Convert the images and labels into numpy arrays
    
    Args:
        input_folder: str 
            Path to the folder containing the images and labels
    '''
    image_dir = os.path.join(input_folder, 'imagesTr')
    if os.listdir(image_dir)[0].endswith('.npz'):
        split_images_and_labels(input_folder)
    elif os.listdir(image_dir)[0].endswith('.nii.gz'):
        convert_niigz_to_numpy(input_folder)
    else:
        raise ValueError('Images format not recognized (should be .npz or .nii.gz)')

def get_resize_shape(input_folder, factor=2):
    '''
    Get the shape to resize the images and labels from the dataset to
    
    Args:
        input_folder: str 
            Path to the folder containing the images and labels
        factor: int
            Factor to resize the images and labels by
    '''
    width_height_mean = 0
    depth_mean = 0
    for subdir in ['imagesTr', 'labelsTr']:
        dir = os.path.join(input_folder, subdir)
        if os.path.isdir(dir):
            for file in tqdm(os.listdir(dir)):
                if file.endswith('.npy'):
                    data = np.load(os.path.join(dir, file))
                    width_height_mean += data.shape[1] + data.shape[2]
                    depth_mean += data.shape[0]
    width_height_mean /= len(os.listdir(dir)) * 2
    depth_mean /= len(os.listdir(dir))
    width_height_mean/=factor
    depth_mean/=factor
    width_height_mean = int(np.ceil(width_height_mean/factor)*factor)
    depth_mean = int(np.ceil(depth_mean/factor)*factor)
    return (depth_mean, width_height_mean, width_height_mean)


def 

if not os.path.exists(output_dataset_path):
    # copy dataset from drive to virtual machine local drive
    shutil.copytree(dataset_folder_path, output_dataset_path)

    # split the data into training and validation sets
    train_images_files, val_images_files, train_labels_files, val_labels_files = train_test_split(
        os.listdir(os.path.join(output_dataset_path, "imagesTr")), 
        os.listdir(os.path.join(output_dataset_path, "labelsTr")), 
        test_size=val_size, 
        random_state=42
    )

    # create train and val folders
    os.makedirs(os.path.join(output_dataset_path, "train"))
    os.makedirs(os.path.join(output_dataset_path, "val"))

    # move validation images and labels to val folder
    for val_im_file, val_label_file in zip(val_images_files, val_labels_files):
        shutil.copyfile(os.path.join(dataset_folder_path, "imagesTr", val_im_file), os.path.join(output_dataset_path, "val", val_im_file))
        shutil.copyfile(os.path.join(dataset_folder_path, "labelsTr", val_label_file), os.path.join(output_dataset_path, "val", val_label_file))
    # move training images and labels to train folder
    for tr_im_file, tr_label_file in zip(train_images_files, train_labels_files):
        shutil.copyfile(os.path.join(dataset_folder_path, "imagesTr", tr_im_file), os.path.join(output_dataset_path, "train", tr_im_file))
        shutil.copyfile(os.path.join(dataset_folder_path, "labelsTr", tr_label_file), os.path.join(output_dataset_path, "train", tr_label_file))

    # renames train files
    for i, (im_tr, la_tr) in enumerate(zip(sorted(train_images_files), sorted(train_labels_files))):
        os.rename(os.path.join(output_dataset_path, "train", im_tr), os.path.join(output_dataset_path, "train", f"image_{str(i).zfill(3)}.npy"))
        os.rename(os.path.join(output_dataset_path, "train", la_tr), os.path.join(output_dataset_path, "train", f"label_{str(i).zfill(3)}.npy"))
    # renames val files
    for i, (im_val, la_val) in enumerate(zip(sorted(val_images_files), sorted(val_labels_files))):
        os.rename(os.path.join(output_dataset_path, "val", im_val), os.path.join(output_dataset_path, "val", f"image_{str(i).zfill(3)}.npy"))
        os.rename(os.path.join(output_dataset_path, "val", la_val), os.path.join(output_dataset_path, "val", f"label_{str(i).zfill(3)}.npy"))

    # remove useless folders
    shutil.rmtree(os.path.join(output_dataset_path, "imagesTr"))
    shutil.rmtree(os.path.join(output_dataset_path, "labelsTr"))