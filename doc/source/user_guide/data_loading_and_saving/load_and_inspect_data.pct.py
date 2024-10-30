#%% [markdown]
# # Download and inspect dataset

#%%
# initialze logging
from tasi.logging import init_logger

init_logger()

#%%
# download dataset
import os
from tasi.dlr.dataset import DLRUTDatasetManager

dataset = DLRUTDatasetManager(DLRUTDatasetManager.VERSIONS.v1_0_0)
path = dataset.load(path='/tmp')
path

#%%
# get available folders
folders = os.listdir(path)
folders


#%% [markdown]
# ## Trajectory Data
# ### Load Trajectory Data
#%%
# get the first file of a folder
def get_first_file(path: str, data_type: str) -> str:
    path = os.path.join(path, data_type)
    files = os.listdir(path)
    files.sort()
    file = os.path.join(path, files[0])
    return file


tj_file = get_first_file(path, 'trajectories')
tj_file

#%%
# load data from csv file as TrajectoryDataset
from tasi.dataset import TrajectoryDataset

ds = TrajectoryDataset.from_csv(tj_file)
ds

# %%
# get type of object
type(ds)

#%% [markdown]
# ### time based analysis

# %%
# get unique timestamps of dataset
ds.timestamps

# %%
# get start and end time of dataset
ds.interval

#%%
# select data between specific timestamps
ds.during(ds.timestamps[0], ds.timestamps[10])

#%% [markdown]
# ### ID based analysis

# %%
# get unique object IDs of dataset
ds.ids

#%%
# filter data of a specific trajectory
ds.trajectory(ds.ids[0])

#%% [markdown]
# ### attribute specific analysis

# %%
# get all available attributes of the dataset
ds.attributes

# %%
# get data of a specific attribute
ds.center

#%%
# get all classification results
ds.classifications

#%%
# get most likely class per row
ds.most_likely_class(by='pose')

#%%
# get most likely class per trajectory (default value)
ds.most_likely_class(by='trajectory')

#%%
# most likely class per trajectory broadcasted to all rows
ds.most_likely_class(by='trajectory', broadcast=True)

#%%
# get all cars of the dataset
ds.get_by_object_class('car')

#%% [markdown]
# ## Traffic Light Data
# ### Load Traffic Light Data

#%%
# choose specifc file
traffic_light_file = get_first_file(path, 'traffic_lights')
traffic_light_file

#%%
# load data from csv
from tasi.dataset import TrafficLightDataset

traffic_lights = TrafficLightDataset.from_csv(traffic_light_file)
traffic_lights

# %%
# filter all state of signal 3
signal = traffic_lights.signal(3)
signal

#%%
# visualize states of a specific signal
signal.plot()

# %%
# get data with signal state 7
traffic_lights.signal_state(7)

#%% [markdown]
# ## Weather Data
# ### Load Weather Data
#%%
# choose specifc file
weather_file = get_first_file(path, 'weather')
weather_file

#%%
# load data from csv file
from tasi.dataset import WeatherDataset

weather = WeatherDataset.from_csv(weather_file)
weather

#%%
# visualize air temperatur over time
weather.air_temperature.plot()

#%% [markdown]
# ## Air Quality Data
# ### Load Air Quality Data
#%%
# choose specifc file
air_quality_file = get_first_file(path, 'air_quality')
air_quality_file

#%%
# load csv file
from tasi.dataset import AirQualityDataset

air_quality = AirQualityDataset.from_csv(air_quality_file)
air_quality

#%%
# get visualize mean air quality
air_quality.mean()

#%% [markdown]
# ## Road Condition Data (Comming Soon)
# ### Load Road Condition Data
# %%
# choose specifc file
# road_condition_file = get_first_file(path, 'road_condition')
# road_condition_file
# #%%
# # load data from csv file
# from tasi.dataset import RoadConditionDataset
# road_conditions = RoadConditionDataset.from_csv(road_condition_file)
# road_conditions
# %%
# visualize surface temperatur over time
# road_conditions.surface_temperature.plot()
