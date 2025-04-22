# %% [markdown]
# # DLR Highway Traffic Dataset (DLR HT)
#
# This example should give a short overview on how to load the [DLR Highway Traffic
# Dataset](https://doi.org/10.5281/zenodo.14012005) which is hosted on Zenodo.
#
# ## Download dataset
#
# At first, we need to download the dataset. For that purpose, helper classes
# are available in `tasi` that we will utilize in the following. In particular,
# since we want to download the DLR HT dataset, we use the. The class contains a
# `tasi.dlr.dataset.DLRHTVersion` enumerator that may be used to
# specify the version of the dataset to download or to get the latest version.
# %%
import os
from tasi.dlr.dataset import DLRHTDatasetManager, DLRHTVersion

dataset = DLRHTDatasetManager(DLRHTVersion.latest)
path = dataset.load()
path
# %% [markdown]
# The dataset is now available in the `/tmp` directory. Let's have
# a look into the dataset and list the available raw data
# %%
raw_data = os.listdir(path.joinpath("raw_data"))
raw_data
# %% [markdown]
# Let's list the available meta data
# %%
meta_data = os.listdir(path.joinpath("meta_data"))
meta_data
# %% [markdown]
# ## Load trajectory data
#
# We can now utilize the `tasi.dlr.dataset.DLRHTTrajectoryDataset` class to load
# the trajectory data from the directory. For demonstration purpose, let's load
# the first batch of the dataset.
# %%
from tasi.dlr import DLRTrajectoryDataset

ds = DLRTrajectoryDataset.from_csv(dataset.trajectory()[0])
ds
# %% [markdown]
# Note that the `Dataset` is represented as a `pandas.DataFrame` since it
# inherits from it. The index of the `Dataset` contains the `timestamp` of a
# traffic participant's state and its `id` as a unique identifier.
#
# The traffic participant's state include various information, including the
# center position, the velocity, dimension and classification type.
#
# ## Load weather data
#
# The DLR Test Bed Lower Saxony is equipped with a weather station that collects
# various information. We can utilize the `tasi.dataset.WeatherDataset` to load
# some of this information.
# %%
from tasi.dlr.dataset import DLRWeatherDataset

weather = DLRWeatherDataset.from_csv(dataset.weather()[0])
weather
# %% [markdown]
# ## Load road quality information
#
# The same weather measurement station also collects information about the road condition.
# %%
from tasi.dlr.dataset import DLRRoadConditionDataset

road_conditions = DLRRoadConditionDataset.from_csv(dataset.road_condition()[0])
road_conditions
# %% [markdown]
# ## Load traffic volume data
#
# The DLR HT dataset contains meta information like traffic volume data that were extracted from the raw data.
# %%
from tasi.dlr.dataset import DLRTrafficVolumeDataset

traffic_volume = DLRTrafficVolumeDataset.from_csv(dataset.traffic_volume()[0])
traffic_volume
# %% [markdown]
# That's it for now. We hope this page helps you get started 😎
