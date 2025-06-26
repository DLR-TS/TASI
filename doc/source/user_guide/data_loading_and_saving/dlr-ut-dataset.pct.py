# %% [markdown]
# # DLR Urban Traffic Dataset (DLR UT)
#
# This example should give a short overview on how to load the [DLR Urban Traffic
# Dataset](https://doi.org/10.5281/zenodo.11396371) which is hosted on Zenodo.
#
# ## Download dataset
#
# At first, we need to download the dataset. For that purpose, the class `DLRUTDatasetManager`
# is available in `tasi` that we will utilize in the following. The class `DLRUTVersion` is an
# enumerator that may be used to specify the version of the dataset to download or to get the latest version.
#
# <div class="alert alert-info">
# The following example will not download the dataset, but will use a local sample that is available in <strong>DATA_PATH</strong>.
# If you want to download the latest version, change to <strong>DLRHTVersion.latest</strong> and update the <strong>path</strong> attribute.
# </div>
# %%
import os

from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion
from tasi.tests import DATA_PATH

dataset = DLRUTDatasetManager(DLRUTVersion.v1_2_0, path=DATA_PATH)
path = dataset.load()
path
# %% [markdown]
# The dataset is now available in the `/tmp` directory. Let's have
# a look into the dataset and list the available traffic information
# %%
folders = os.listdir(path)
folders
# %% [markdown]
# ## Load trajectory data
#
# We can now utilize the `tasi.dlr.dataset.DLRTrajectoryDataset` class to load
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
# boundingbox position, the velocity, dimension and classification type.
#
# ## Load traffic light data
#
# The DLR UT dataset also contains information of the traffic lights. We utilize
# the `tasi.dlr.dataset.DLRTrajectoryDataset` class to load the information.
# For demonstration purpose, let's load the first batch of the dataset.
# %%
from tasi.dlr import DLRUTTrafficLightDataset

traffic_lights = DLRUTTrafficLightDataset.from_csv(dataset.traffic_lights()[0])
traffic_lights
# %% [markdown]
# ### Load weather data
#
# The DLR Research Intersection is equipped with a weather station stat collects
# various information. We can utilize the `tasi.dataset.WeatherDataset` to load
# some of this information.
# %%
from tasi.dlr.dataset import DLRWeatherDataset

weather = DLRWeatherDataset.from_csv(dataset.weather()[0])
weather
# %% [markdown]
# ## Load air quality data
#
# Although also collected by the same weather station, information about the
# local air quality is available via another dataset.
# %%
from tasi.dlr.dataset import DLRAirQualityDataset

air_quality = DLRAirQualityDataset.from_csv(dataset.air_quality()[0])
air_quality
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
# The DLR UT dataset contains meta information like traffic volume data that were extracted from the raw trajectory data.
# %%
from tasi.dlr.dataset import DLRTrafficVolumeDataset

traffic_volume = DLRTrafficVolumeDataset.from_csv(dataset.traffic_volume()[0])
traffic_volume
# %% [markdown]
# ## Load OpenSCENARIO files
#
# The DLR UT dataset contains the trajectory data in OpenSCENARIO format.
# %%
openscenario_files = dataset.openscenario()
openscenario_files
# %% [markdown]
# That's it for now. We hope this page helps you get started 😎
