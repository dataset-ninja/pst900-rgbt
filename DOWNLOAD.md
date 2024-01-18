Dataset **PST900 RGB-T** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/D/7/Kv/wj9mXgrRyX5KgLtP1jU45q7HygHt2yA5h6XFIxI0EYRlFeEq0KKiyRgpoNHOLiNZSih6FRf9atgLXIWXXNDQF0ZeRfD92OahU7jdZ1z7AQGuzd4PHzbBmDPVCHQ9.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='PST900 RGB-T', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://drive.google.com/open?id=1hZeM-MvdUC_Btyok7mdF00RV-InbAadm).