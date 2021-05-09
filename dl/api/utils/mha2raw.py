import matplotlib.pyplot as plt
import numpy as np
import SimpleITK
from api.utils.config import Config as cfg


mha_dir = "../data/test.mha";

if __name__ == "__main__":
    img = SimpleITK.ReadImage(mha_dir);
    raw = SimpleITK.GetArrayFromImage(img);