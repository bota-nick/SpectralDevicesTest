# SpectralDevicesTest

Exploration notebook for multispectral imagery from the Spectral Devices MSDC-2-4-CUS4-005 camera system.

## Camera bands

| Camera | Band | Central Wavelength | FWHM |
|--------|------|--------------------|------|
| RGB | Green | 540 nm | 60 nm |
| RGB | Blue | 470 nm | 60 nm |
| RGB | Red | 630 nm | 60 nm |
| RGB | Green2 | 540 nm | 60 nm |
| BIO | NIR1 | 735 nm | 25 nm |
| BIO | NIR2 | 800 nm | 25 nm |
| BIO | NIR3 | 865 nm | 25 nm |
| BIO | NIR4 | 930 nm | 25 nm |
| SWIR | — | 1125 nm | — |
| SWIR | — | 1275 nm | — |

## Run on Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/imampurwadi/SpectralDevicesTest/blob/main/explore.ipynb)

## Local setup

```bash
conda activate new_cle
jupyter notebook explore.ipynb
```
