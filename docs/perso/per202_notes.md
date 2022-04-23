## 2021-11-23

Tried to install esem, cis and gpflow in an existing conda environment (ai4w_tf) but this was a mistake. Some clashes of versions with TF required by ai4water, numpy, tensorflow, etc. The usual python experience. 

So, create yet again a new environment:

```sh
conda create -n esem python=3.9 mamba -c conda-forge
conda activate esem
mamba install -c conda-forge cis
pip install esem gpflow keras scikit-learn
```

