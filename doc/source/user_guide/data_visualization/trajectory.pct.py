# %% [markdown]
# # Visualization of trajectories
# If we work with trajectory data, we often want to visualize them from a
# so called `birds eye view`. The following example demonstrates how to achieve
# this with `tasi` using the [DLR Urban Traffic Dataset](https://doi.org/10.5281/zenodo.11396371).
#
# ## Load trajectories
# At first, let's load trajectories from the DLR dataset.
# %%
from tasi.dlr.dataset import DLRUTDatasetManager, DLRUTVersion
from tasi.dlr import DLRTrajectoryDataset

dataset = DLRUTDatasetManager(DLRUTVersion.latest)
# select a trajectory file from the middle of the dataset to include data from all object classes
ut = DLRTrajectoryDataset.from_csv(dataset.trajectory()[48])
ut
# %% [markdown]
# ## Plot trajectories
# We now utilize the `TrajectoryPlotter` to visualize the trajectories of the
# traffic participants that we've loaded.
# %%
from tasi.plotting import TrajectoryPlotter
import matplotlib.pyplot as plt

f, ax = plt.subplots()

plotter = TrajectoryPlotter()
plotter.plot(ut, ax=ax)
# %% [markdown]
# ### Change trajectory color
# Note that the trajectories are colorized with the default color which we can
# change so any arbitrary color, such as `lightgray`.
# %%
f, ax = plt.subplots()
plotter.plot(ut, ax=ax, color="lightgray")
# %% [markdown]
# ### Change color of a specific trajectory
# You can also define the color of a specific trajectory.
# %%
f, ax = plt.subplots()
plotter.plot(ut, ax=ax, color="black", trajectory_kwargs={
    ut.ids[-20]: {
        "color": "red"
    }
})
# %% [markdown]
# ### Change trajectory opacity
# or even change the opacity of each trajectory to quickly get an overview of
# the traffic density. Let's change the opacity to 20% via the `alpha` argument.
# %%
f, ax = plt.subplots()
plotter.plot(ut, ax=ax, alpha=0.2)
# %% [markdown]
# The plot already indicates the various traffic volumes on the different routes
# at the intersection.
# %% [markdown]
# ## Plot DLR UT trajectories on orthophoto
# We can also combine the `TrajectoryPlotter` with the `BoundingboxPlotter` to
# visualize trajectories on an orthophoto.
# %%
import numpy as np
from tasi.plotting import BoundingboxPlotter, LowerSaxonyOrthophotoTile

f, ax = plt.subplots()

# plot the orthophoto first
bbox_plotter = BoundingboxPlotter(ut.roi, LowerSaxonyOrthophotoTile())
bbox_plotter.plot(ax)

# and the trajectories on top
tj_plotter = TrajectoryPlotter()
tj_plotter.plot(ut, ax=ax)

# hide the axis
_ = ax.axis("off")
# %% [markdown]
# Note that it may become hard to see the trajectories on the background.
# To increase the contrast, we can adapt the opacity of the ortophoto via the
# `alpha` argument. Let's set is to 0.5 (50%) to highlight the trajectories.
# %%
f, ax = plt.subplots()

bbox_plotter.plot(ax, alpha=0.5)
tj_plotter.plot(ut, ax=ax, alpha=0.25)

_ = ax.axis("off")

# %% [markdown]
# ## Plot DLR HT trajectories on orthophoto
# We can also use the `TrajectoryPlotter` with the `BoundingboxPlotter` to
# visualize trajectories of the DLR HT dataset on an orthophoto. Let's load
# and plot the trajectories from the DLR HT dataset. This time, let's use the
# DLRTrajectoryPlotter to color the trajectories in default DLR-colors.
# %%
from tasi.dlr.dataset import DLRHTDatasetManager, DLRHTVersion
from tasi.dlr.plotting import DLRTrajectoryPlotter

# load dataset
dataset = DLRHTDatasetManager(DLRHTVersion.latest)
path = dataset.load()
# use 3 as it contains objects from all object classes
ht = DLRTrajectoryDataset.from_csv(dataset.trajectory()[3])

f, ax = plt.subplots()

# plot the orthophoto first
bbox_plotter = BoundingboxPlotter(ht.roi, LowerSaxonyOrthophotoTile())
bbox_plotter.plot(ax)

# and the trajectories on top
tj_plotter = DLRTrajectoryPlotter()
tj_plotter.plot(ht, ax=ax)

# hide the axis
_ = ax.axis("off")
