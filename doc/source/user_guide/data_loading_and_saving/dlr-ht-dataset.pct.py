# %% [markdown]
# # DLR Highway Traffic Dataset (DLR HT)
#
# This example should give a short overview on how to load the [DLR Highway Traffic
# Dataset](https://zenodo.org/records/14012006) which is hosted on Zenodo.
#
# ## Download dataset
#
# At first, we need to download the dataset. For that purpose, helper classes
# are available in `tasi` that we will utilize in the following. In particular,
# since we want to download the DLR HT dataset, we use the. The class contains a
# `tasi.dlr.dataset.DLRHTVersion` enumerator that may be used to
# specify the version of the dataset to download.
# %%
import os
from tasi.dlr.dataset import DLRHTDatasetManager, DLRHTVersion

dataset = DLRHTDatasetManager(DLRHTVersion.v1_0_0)
path = dataset.load(path="/tmp")
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

ds = DLRTrajectoryDataset.from_csv(dataset.trajectory("/tmp")[0])
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
from tasi.dataset import WeatherDataset

weather = WeatherDataset.from_csv(dataset.weather("/tmp")[0])
weather
# %% [markdown]
# ## Load road quality information
#
# The same weather measurement station also collects information about the road condition.
# %%
from tasi.dataset import RoadConditionDataset

road_conditions = RoadConditionDataset.from_csv(dataset.road_condition("/tmp")[0])
road_conditions
# %% [markdown]
# ## Load traffic volume data
#
# The DLR HT dataset contains meta information like traffic volume data that were extracted from the raw data.
# %%
from tasi.dataset import TrafficVolumeDataset

traffic_volume = TrafficVolumeDataset.from_csv(dataset.traffic_volume("/tmp")[0])
traffic_volume
# %% [markdown]
# That's it for now. We hope this page helps you get started 😎
