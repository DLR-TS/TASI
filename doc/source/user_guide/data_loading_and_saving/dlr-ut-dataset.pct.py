#%% [markdown]
# # DLR Urban Traffic Dataset (DLR UT)
#
# This example should give a short overview on how to load the [DLR Urban Traffic
# Dataset](https://doi.org/10.5281/zenodo.11396371) which is hosted on Zenodo.
#
# ## Download dataset
#
# At first, we need to download the dataset. For that purpose, helper classes
# are available in `tasi` that we will utilize in the following. In particular,
# since we want to download the DLR UT dataset, we use the. The class contains a
# `tasi.dlr.dataset.DLRUTVersion` enumerator that may be used to
# specify the version of the dataset to download.
# %%
import os
from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion

dataset = DLRUTDatasetManager(DLRUTVersion.v1_2_0)
path = dataset.load(path='/tmp')
path
#%% [markdown]
# The dataset is now available in the `/tmp` directory. Let's have
# a look into the dataset and list the available traffic information
#%%
folders = os.listdir(path)
folders
#%% [markdown]
# ## Load trajectory data
#
# We can now utilize the `tasi.dlr.dataset.DLRTrajectoryDataset` class to load
# the trajectory data from the directory. For demonstration purpose, let's load
# the first batch of the dataset.
#%%
from tasi.dlr import DLRTrajectoryDataset

ds = DLRTrajectoryDataset.from_csv(dataset.trajectory("/tmp")[0])
ds
#%% [markdown]
# Note that the `Dataset` is represented as a `pandas.DataFrame` since it
# inherits from it. The index of the `Dataset` contains the `timestamp` of a
# traffic participant's state and its `id` as a unique identifier.
#
# The traffic participant's state include various information, including the
# center position, the velocity, dimension and classification type.
#
# ## Load traffic light data
#
# The DLR UT dataset also contains information of the traffic lights. We utilize
# the `tasi.dlr.dataset.DLRTrajectoryDataset` class to load the information.
# For demonstration purpose, let's load the first batch of the dataset.
#%%
from tasi.dlr import DLRUTTrafficLightDataset

traffic_lights = DLRUTTrafficLightDataset.from_csv(dataset.traffic_lights("/tmp")[0])
traffic_lights
#%% [markdown]
# ### Load weather data
#
# The DLR Research Intersection is equipped with a weather station stat collects
# various information. We can utilize the `tasi.dataset.WeatherDataset` to load
# some of this information.
#%%
from tasi.dataset import WeatherDataset

weather = WeatherDataset.from_csv(dataset.weather("/tmp")[0])
weather
#%% [markdown]
# ## Load air quality data
#
# Although also collected by the same weather station, information about the
# local air quality is available via another dataset.
#%%
from tasi.dataset import AirQualityDataset

air_quality = AirQualityDataset.from_csv(dataset.air_quality("/tmp")[0])
air_quality
#%% [markdown]
# ## Load road quality information
#
# The same weather measurement station also collects information about the road condition.
#%%
from tasi.dataset import RoadConditionDataset

road_conditions = RoadConditionDataset.from_csv(dataset.road_condition("/tmp")[0])
road_conditions
# %% [markdown]
# ## Load traffic volume data
#
# The DLR UT dataset contains meta information like traffic volume data that were extracted from the raw trajectory data.
# %%
from tasi.dataset import TrafficVolumeDataset

traffic_volume = TrafficVolumeDataset.from_csv(dataset.traffic_volume("/tmp")[0])
traffic_volume
# %% [markdown]
# ## Load OpenSCENARIO files
#
# The DLR UT dataset contains the trajectory data in OpenSCENARIO format.
# %%
from tasi.dataset import TrafficVolumeDataset

openscenario_files = dataset.openscenario("/tmp")
openscenario_files

#%% [markdown]
# That's it for now. We hope this page helps you get started 😎
