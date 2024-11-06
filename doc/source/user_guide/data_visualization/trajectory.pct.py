#%% [markdown]
# # Visualization of trajectories
# If we work with trajectory data, we often want to visualize them from a
# so called `birds eye view`. The following example demonstrates how to achieve
# this with `tasi` using the [Urban Traffic
# Dataset](https://zenodo.org/records/11396372).
#
# ## Load trajectories
# At first, let's load trajectories from the DLR dataset.
#%%
from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion
from tasi.dlr import DLRUTTrajectoryDataset

dataset = DLRUTDatasetManager(DLRUTVersion.v1_1_0)
ds = DLRUTTrajectoryDataset.from_csv(dataset.trajectory("/tmp")[0])
#%% [markdown]
# ## Plot trajectories
# We now utilize the `TrajectoryPlotter` to visualize the trajectories of the
# traffic participants that we've loaded. 
#%%
from tasi.plotting import TrajectoryPlotter
import matplotlib.pyplot as plt 

f, ax = plt.subplots()

plotter = TrajectoryPlotter()
plotter.plot(ds, ax=ax)
#%% [markdown]
# ### Change trajectory color
# Note that the trajectories are colorized with the default color which we can
# change so any arbitrary color, such as `lightgray`.
#%%
f, ax = plt.subplots()
plotter.plot(ds, ax=ax, color='lightgray')
#%% [markdown]
# ### Change trajectory opacity
# or even change the opacity of each trajectory to quickly get an overview of
# the traffic density. Let's change the opacity to 10% via the `alpha` argument
# and set the color to `black`.
#%%
f, ax = plt.subplots()
plotter.plot(ds, ax=ax, color='black', alpha=0.1)
#%% [markdown]
# The plot already indicates the various traffic volumes on the different routes
# at the intersection.
#%% [markdown]
# ## Plot trajectories on orthophoto
# We can also combine the `TrajectoryPlotter` with the `BoundingboxPlotter` to
# visualize trajectories on an orthophoto.
#%%
import numpy as np 
from tasi.plotting import BoundingboxPlotter, LowerSaxonyOrthophotoTile

f, ax = plt.subplots()

# plot the orthophoto first
roi = np.array([604675, 5792680, 604875, 5792870]).reshape(-1, 2)

plotter = BoundingboxPlotter(roi, LowerSaxonyOrthophotoTile())
plotter.plot(ax)

# and the trajectories on top
tj_plotter = TrajectoryPlotter()
tj_plotter.plot(ds, ax=ax, color='black')

# hide the axis
_ = ax.axis('off')
#%% [markdown]
# Note that it may become hard to see the trajectories on the background.
# To increase the contrast, we can adapt the opacity of the ortophoto via the
# `alpha` argument. Let's set is to 0.5 (50%) to highlight the trajectories.
#%%

f, ax = plt.subplots()

plotter.plot(ax, alpha=0.5)
tj_plotter.plot(ds, ax=ax, color='black', alpha=0.25)

_ = ax.axis('off')