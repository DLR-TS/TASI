#%% [markdown]
# # Using the DLRUTDataset
#
# This example shall give an overview of the methods and attributes that are
# available in the `DLRUTDataset` class.
#
# ## Load trajectory data
# At first, we need to load the trajectory data of the dataset. 
# %%
from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion
from tasi.dlr import DLRUTTrajectoryDataset

dataset = DLRUTDatasetManager(DLRUTVersion.v1_1_0)
dataset.load("/tmp")

ds = DLRUTTrajectoryDataset.from_csv(dataset.trajectory("/tmp")[50])

#%% [markdown]
# ## Attributes of the dataset
# There are several attributes available to get information about a dataset. For
# instance, we can get the interval of a dataset via the property
#%%
ds.interval
#%% [markdown]
# or all unique timestamps of it via
#%%
ds.timestamps
#%% [markdown]
# or the ids of all traffic participants in the dataset.
#%%
ds.ids
#%% [markdown]
# ## Filtering
# If you want to look into a short sequence of the overall dataset, you can
# select specific rows of the overall dataset. The `DLRUTTrajectoryDataset`
# provides various ways for this purpose. 
#
# ### Time and object
# There are two variants to filter a dataset based on the information on the
# dataset's `index`. For instance, if you want to filterthe dataset by an
# interval, you can utilize the `during` method 
# %%
ds.during(ds.timestamps[0], ds.timestamps[10])
#%% [markdown]
# that returns the rows within the given interval. 
#
# Another variant to select specific rows of the datasets is by the `id` of a
# traffic participant. This might be useful if you want to take a closer look
# into the behavior of specific traffic participants. For instance, to filter by
# the second traffic participant in the dataset, we can combine the `ids`
# attribute with the `trajectory` method. 
#%%
ds.trajectory(ds.ids[1])

#%% [markdown]
# ### Traffic participant properties
# 
# There are also methods available that might help to find the relevant
# information in the dataset. The most straight forward option is to use pandas'
# capability to access specific attributes` of the datasets. The available attributes on the dataset, are available via the `attribute` property.
#%%
ds.attributes
#%% [markdown]
# We can, for instance, access the traffic participants `center` position.
#%%
ds.center
#%% [markdown]
# or the classification propabilities.
#%%
ds.classifications
#%% [markdown]
# We extended these basic capabilities with additional methods, that, for instance, allow to get the most likely class by each traffic participant's pose
#%%
ds.most_likely_class(by='pose')
#%% [markdown]
# or by the overall trajectory (the default), i.e. all poses of a traffic participants.
#%%
ds.most_likely_class(by='trajectory')
#%% [markdown] 
# This might help to filter the dataset to select only traffic participants that
# are classified as a `car`. To archieve this, we first get the most likely
# class per trajectory, select the rows having the value 'car' and pass their
# index (the traffic particpant's `id`) into the `trajectory` method of the
# `Dataset`.
#%%
classification = ds.most_likely_class(by='trajectory')

ds.trajectory(classification[classification == 'car'].index)
