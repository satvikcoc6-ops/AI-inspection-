# MDM defect inspection — first trained baseline

This package contains a PatchCore anomaly detection model fitted to the normal
metal-nut images in MVTec AD. It uses a pretrained ResNet18 feature extractor and
a learned memory bank of normal patches. It does not train a language model,
classify defect types, or establish automotive quality acceptance.

## Start here (no retraining needed)

An optional Google Colab notebook, Try_Model_in_Colab.ipynb, is included. Open it
in Colab and follow its cells, uploading this ZIP when prompted. It avoids local
installation. The local prediction commands below were executed and checked;
the Colab notebook is provided as an unexecuted convenience wrapper.

1. Extract this ZIP into a folder.
2. Install Python 3.12 and open a terminal in the extracted folder.
3. Run `python -m pip install -r requirements.txt` (internet required).
4. Run `python predict.py examples/scratch.png --output my_result`.
5. Open `my_result/heatmap_overlay.png` and `my_result/result.json`.

The included scratch example is a documented failure: this model scores it below
the anomaly decision threshold and misses the defect. It was selected as the first
scratch image in the held-out manifest, not selected to produce a good result.
This illustrates why the model must not be used as an automatic acceptance system.
Measured test image F1 is 0.964, image AUROC is 0.983; see evaluation.json.

Red areas in the overlay represent higher anomaly scores. A score is NOT a
probability, a defect severity, or a physical measurement. The first image should
look like the training data: a single metal nut in a comparable camera view and
background. Arbitrary car photographs are outside this model's scope.

## What was trained

- Dataset: MVTec AD, metal_nut category, 220 normal training images.
- Feature extraction: pretrained ResNet18, layer2 and layer3, 256x256 input.
- Learning: PatchCore memory bank, 1% coreset, three nearest neighbours.
- Seed: 42. Validation: 25% of the original test split, separately held out.
- Remaining test images are not used to fit the memory bank or select thresholds.
- This custom split is not a claim of performance on the complete official benchmark.
- Evaluation metrics and actual split sizes are in evaluation.json.
- Reproducibility lists are in the CSV manifests (paths refer to the training machine).

## Files

- metal_nut_patchcore.ckpt: fitted model and normal patch memory bank.
- predict.py: reload the saved model and inspect a photograph.
- train.py: reproduce training and evaluation.
- evaluation.json: measured held-out performance, not promised performance.
- examples/: sample input images and prediction outputs.
- requirements.txt: primary package versions used for this run.

## Reproduce training

Download metal_nut.tar.xz from the official MVTec AD downloads page and extract
it so that data/metal_nut/train/good and data/metal_nut/test exist. Then run
`python train.py`. Training requires downloading pretrained backbone weights.
The dataset is not included in full. CPU training works; a GPU is optional.

## Next stage for your project

Validate with photographs of your own components; collect representative normal
and defective samples. Train defect classification/segmentation if you need the
system to name scratches, cracks, dents, or weld irregularities. Add reviewed
GenAI reporting only after those outputs are validated. No GenAI reporting
component is included in this first baseline.

## Dataset attribution and terms

Source: https://www.mvtec.com/research-teaching/datasets/mvtec-ad
Official downloads: https://www.mvtec.com/company/research/datasets/mvtec-ad/downloads
MVTec AD by Paul Bergmann, Michael Fauser, David Sattlegger and Carsten Steger,
CVPR 2019; extended dataset paper IJCV 2021, DOI 10.1007/s11263-020-01400-4.
Dataset and included sample image derivatives: CC BY-NC-SA 4.0,
https://creativecommons.org/licenses/by-nc-sa/4.0/ . Noncommercial educational use;
retain attribution and applicable share-alike terms. No endorsement is implied.
Anomalib is Apache-2.0; see https://github.com/open-edge-platform/anomalib .
The newly authored scripts in this package are offered under MIT terms.
Use checkpoint files only from trusted sources; loading serialized models can execute code.
