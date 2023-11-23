# https://github.com/ShreyasSkandanS/pst900_thermal_rgb

import os
import shutil
from urllib.parse import unquote, urlparse

import numpy as np
import supervisely as sly
from cv2 import connectedComponents
from dotenv import load_dotenv
from supervisely.io.fs import (
    dir_exists,
    file_exists,
    get_file_ext,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s
from dataset_tools.convert import unpack_if_archive


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # project_name = "PST900 RGB-T"
    dataset_path = "/mnt/d/datasetninja-raw/pst900-rgbt/PST900_RGBT_Dataset/PST900_RGBT_Dataset"
    batch_size = 20
    images_folder = "rgb"
    depths_folder = "depth"
    masks_folder = "labels"
    thermal_folder = "thermal"
    thermal_raw_folder = "thermal_raw"
    group_tag_name = "im_id"

    def create_ann(image_path):
        labels = []
        tags = []

        id_data = get_file_name(image_path)
        group_id = sly.Tag(tag_id, value=id_data)
        tags.append(group_id)

        image_name = get_file_name_with_ext(image_path)

        mask_path = os.path.join(masks_path, image_name)
        if file_exists(mask_path):
            mask_np = sly.imaging.image.read(mask_path)[:, :, 0]
            img_height = mask_np.shape[0]
            img_wight = mask_np.shape[1]
            unique_pixels = np.unique(mask_np)[1:]
            for pixel in unique_pixels:
                obj_class = idx_to_class[pixel]
                mask = mask_np == pixel
                ret, curr_mask = connectedComponents(mask.astype("uint8"), connectivity=8)
                for i in range(1, ret):
                    obj_mask = curr_mask == i
                    curr_bitmap = sly.Bitmap(obj_mask)
                    if curr_bitmap.area > 30:
                        curr_label = sly.Label(curr_bitmap, obj_class)
                        labels.append(curr_label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    # https://github.com/ShreyasSkandanS/pst900_thermal_rgb/blob/master/pstnet/code/pst_inference.py - for classnames
    fire = sly.ObjClass("fire extinguisher", sly.Bitmap)
    backpack = sly.ObjClass("backpack", sly.Bitmap)
    hand_drill = sly.ObjClass("hand drill", sly.Bitmap)
    randy = sly.ObjClass("rescue randy", sly.Bitmap)

    idx_to_class = {1: fire, 2: backpack, 3: hand_drill, 4: randy}

    tag_id = sly.TagMeta("im_id", sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=[fire, backpack, hand_drill, randy], tag_metas=[tag_id])
    api.project.update_meta(project.id, meta.to_json())
    api.project.images_grouping(id=project.id, enable=True, tag_name=group_tag_name)

    for ds_name in os.listdir(dataset_path):
        ds_path = os.path.join(dataset_path, ds_name)

        images_path = os.path.join(ds_path, images_folder)
        depths_path = os.path.join(ds_path, depths_folder)
        masks_path = os.path.join(ds_path, masks_folder)
        thermal_path = os.path.join(ds_path, thermal_folder)
        thermal_raw_path = os.path.join(ds_path, thermal_raw_folder)

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        for curr_images_path in [images_path, depths_path, thermal_path, thermal_raw_path]:
            images_names = [im_name for im_name in os.listdir(curr_images_path)]

            progress = sly.Progress(
                "Create dataset {}, add {} data".format(ds_name, curr_images_path.split("/")[-1]),
                len(images_names),
            )

            for images_names_batch in sly.batched(images_names, batch_size=batch_size):
                img_pathes_batch = [
                    os.path.join(curr_images_path, image_name) for image_name in images_names_batch
                ]

                images_names_batch = [
                    curr_images_path.split("/")[-1] + "_" + get_file_name_with_ext(im_path)
                    for im_path in img_pathes_batch
                ]

                img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
                img_ids = [im_info.id for im_info in img_infos]

                anns = [create_ann(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns)

                progress.iters_done_report(len(images_names_batch))
    return project
