**PST900 RGB-T: Penn Subterranean Thermal 900 RGB-Thermal Dataset** is a dataset for instance segmentation, semantic segmentation, and object detection tasks. It is used in the robotics industry. 

The dataset consists of 3540 images with 5452 labeled objects belonging to 4 different classes including *backpack*, *rescue randy*, *hand drill*, and other: *fire extinguisher*.

Images in the PST900 RGB-T dataset have pixel-level instance segmentation annotations. Due to the nature of the instance segmentation task, it can be automatically transformed into a semantic segmentation (only one mask for every class) or object detection (bounding boxes for every object) tasks. There are 516 (15% of the total) unlabeled images (i.e. without annotations). There are 2 splits in the dataset: *train* (2388 images) and *test* (1152 images). Every quartet of images (RGB, depth, thermal, and thermal_raw) has ***im_id*** tag. The dataset was released in 2020 by the <span style="font-weight: 600; color: grey; border-bottom: 1px dashed #d3d3d3;">University of Pennsylvania, USA</span>.

<img src="https://github.com/dataset-ninja/pst900-rgbt/raw/main/visualizations/poster.png">
