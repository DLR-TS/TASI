# %% [markdown]
# # How to get data into TASI?
#
# To get things started with `TASI` and other traffic data than the [DLR
# UT](https://doi.org/10.5281/zenodo.11396371) and [DLR
# HT](https://doi.org/10.5281/zenodo.14012005) dataset, the `tasi.io.public`
# package is the first starting point and should be used to ensure proper
# conversion between data formats.
#
# The following example demonstrates how to initialize a `tasi.Pose` and
# `tasi.Trajectory` via the *pydantic* interface.
#
# ## Initialize a traffic participant
# At first, we create representation of the traffic participant. It is the
# representation of a particular traffic participant over time. Please note that
# there is no direct representation of a `TrafficParticipant` using the `TASI`
# internal representation.
# %%
import tasi.io as tio

dimension = tio.Dimension(width=0.75, height=1.85, length=0.5)

tp = tio.TrafficParticipant(
    classifications=tio.Classifications(pedestrian=1),
    dimension=dimension,
    id_object=1,
)
tp
# %% [markdown]
# The traffic participant is already fully defined by an index.
# All other attributes are optional, since they may not be available when the
# traffic participant is seen for the first time. Besides a unique identifier,
# we define the `Dimension` of the traffic participant and indicate that we are
# sure that this is a pedestrian via the `Classifications` attribute.
#
# ## Initialize a pose
# While the `TrafficParticipant` allows to manage information over time, the
# `Pose` is used to describe the state for a particular time. Let's assume that
# we can measure the state of the object and want to denote this as a `Pose`. In
# the following, we define a `Pose` with a position at UTM (604748, 5792815)
# walking eastward with a velocity of $7\frac{km}{h}$. We can create the
# `BoundingBox` from the dimension, position and orientation.
#
# %%
from datetime import datetime

import numpy as np

position = tio.Position(easting=604748, northing=5792815, altitude=0)
orientation: tio.Orientation = np.deg2rad(15)

p = tio.PosePublic(
    dimension=dimension,
    position=position,
    velocity=tio.Velocity.from_magnitude(7 / 3.6, orientation),
    acceleration=tio.Acceleration(),
    boundingbox=tio.BoundingBox.from_dimension(
        dimension, relative_to=position, orientation=orientation
    ),
    classifications=tio.Classifications(pedestrian=1),
    traffic_participant=tp,
    timestamp=datetime.now(),
    orientation=orientation,
)
p
# %% [markdown]
# Please note that both, a reference point and the orientation
# should be used to create the boundingbox, since it is assumed that the points
# of the boundingbox are also UTM positions.
# %%
p.boundingbox
# %% [markdown]
# ## Initialize a trajectory
# For the sake of simplicity, let's create multiple poses where the object just
# moves forward.
# %%

from datetime import timedelta

dt = 1  # 1 second between measurements


def init_pose(pose: tio.PosePublic):
    pose_ = pose.model_copy(deep=True)

    # update the position only w.r.t the velocity
    pose_.position += pose_.velocity * dt  # type: ignore

    # Note that the boundingbox has become invalid. Let's recreate it
    pose_.boundingbox = tio.BoundingBox.from_dimension(
        dimension, relative_to=pose_.position, orientation=orientation
    )

    pose_.timestamp += timedelta(seconds=dt)

    return pose_


poses = []
for i in range(11):
    p = init_pose(p)
    poses.append(p)

# %% [markdown]
# We can use the poses and the traffic participant to create a trajectory.
# %%
tj = tio.TrajectoryPublic(poses=poses, traffic_participant=tp)
tj
# %% [markdown]
# ## Convert to numerical representation
#
# The final step is now to create the trajectory to the numerical representation
# format, i.e., the pandas-based format. For this purpose, all public models
# available via `tasi.io` implement the `as_tasi()` method. Let's try it out
# with the trajectory we created above.
# %%
tjn = tj.as_tasi()
tjn
# %% [markdown]
# The trajectory is now represented using the tabular-style format
# of pandas. The traffic participant's index and the pose' timestamp are on the
# `DataFrame` index. The other pose information are available via the table
# columns.
#
# ## Trajectory visualization
# Since the trajectory is now available using the internal format, we can easily
# plot it.
# %%
import matplotlib.pyplot as plt
import numpy as np

from tasi import TrajectoryDataset
from tasi.plotting import TrajectoryPlotter

# the following is only possible if tasi[wms] is installed
from tasi.plotting.wms import BoundingboxPlotter, LowerSaxonyOrthophotoTile

f, ax = plt.subplots(figsize=(8, 8))

roi = np.array([604720, 5792765, 604820, 5792830]).reshape(-1, 2)

plotter = BoundingboxPlotter(roi, LowerSaxonyOrthophotoTile())
plotter.plot(ax)

plotter = TrajectoryPlotter()
plotter.plot(TrajectoryDataset.from_trajectories([tjn]))
# %% [markdown]
# That's it for now. You should now be able to get your data converted to
# `TASI` 😀.
