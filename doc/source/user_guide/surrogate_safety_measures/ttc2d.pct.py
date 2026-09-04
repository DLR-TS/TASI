# %% [markdown]
# # Generalized Time-to-Collision for crossing paths (TTC2D)
#
# `TTC2D` generalizes `TTC` from straight-line car-following to *any* two participants moving freely in
# the 2D plane - e.g. at an intersection, where their paths cross at an angle instead of running parallel.
# It models both participants as circles and predicts, at every sampled timestep, when (if ever) the two
# circles would first touch, assuming each continues at its current velocity from that instant onward.
#
# **Definition**, adapted from Li, S., Anis, M., Lord, D., Zhang, H., Zhou, Y., & Ye, X. (2024), "Beyond 1D
# and oversimplified kinematics: A generic analytical framework for surrogate safety measures," Accident
# Analysis & Prevention, 199, 107531: let `dp(t) = challenger.position(t) - ego.position(t)` and
# `dv(t) = challenger.velocity(t) - ego.velocity(t)` (both 2D vectors), and `R = r_ego + r_challenger` with
# `r = dimension.length / 2` for each participant (a simplification: the vehicle's half-length as its
# radius). `TTC2D(t)` is the smallest non-negative real root `tau` of::
#
#     (dv . dv) * tau ** 2 + 2 * (dp . dv) * tau + (dp . dp - R ** 2) = 0
#
# ## A plausible crossing interaction
#
# Two cars head toward the same intersection point on a collision course: `ego` drives east at 12 m/s
# starting 36 m west of it, `challenger` drives north at 10 m/s starting 30 m south of it - both would
# reach that exact point at `t=3s` if neither reacted. Both cars are 4.5 m long.
# %%
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from tasi import Trajectory
from tasi.io import (
    Acceleration,
    BoundingBox,
    Classifications,
    Dimension,
    PosePublic,
    Position,
    TrafficParticipant,
    TrajectoryPublic,
    Velocity,
)
from tasi.smos import TTC2D

T0 = datetime(2024, 1, 1, 12, 0, 0)
DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)
CLASSIFICATIONS = Classifications(car=1.0)


def make_trajectory(id_object, origin, velocity, n_steps=3, dt=1.0):
    """Build a straight, constant-velocity `Trajectory` for a car of `DIMENSION`."""
    tp = TrafficParticipant(id_object=id_object, classifications=CLASSIFICATIONS, dimension=DIMENSION)
    poses = []
    for i in range(n_steps):
        t = i * dt
        position = Position(easting=origin[0] + velocity[0] * t, northing=origin[1] + velocity[1] * t)
        poses.append(
            PosePublic(
                timestamp=T0 + timedelta(seconds=t),
                position=position,
                orientation=0.0,
                traffic_participant=tp,
                dimension=DIMENSION,
                velocity=Velocity(x=velocity[0], y=velocity[1]),
                acceleration=Acceleration(),
                classifications=CLASSIFICATIONS,
                boundingbox=BoundingBox.from_dimension(DIMENSION, relative_to=position),
            )
        )
    return TrajectoryPublic(poses=poses, traffic_participant=tp).as_tasi()


ego = make_trajectory(id_object=1, origin=(-36.0, 0.0), velocity=(12.0, 0.0))
challenger = make_trajectory(id_object=2, origin=(0.0, -30.0), velocity=(0.0, 10.0))

ego.position[["easting", "northing"]]
# %% [markdown]
# We only sample `t=0,1,2` here (staying well before the predicted `t=3s` encounter) - `TTC2D`'s formula
# measures distance between raw *positions*, so once the two are exactly co-located its "smallest
# non-negative root" starts picking up the moment they'd separate again rather than 0, which is a
# confusing edge case to show in an introductory example.
#
# ## Computing TTC2D
# %%
ttc2d = TTC2D.estimate(ego, challenger)
pd.Series(ttc2d.values, index=ttc2d.timestamps, name="TTC2D [s]")
# %% [markdown]
# TTC2D decreases by exactly 1 s per second (2.71 s, 1.71 s, 0.71 s) - expected, since both participants
# move at constant velocity on an unchanging collision course, so the predicted time to collision simply
# counts down in step with the passage of time itself.
#
# ## Reproducing the value by hand
#
# Let's verify the value at `t=0s` (index 0) from the raw numbers `TTC2D.estimate` used internally.
# %%
i = 0

ego_position = ego.position[["easting", "northing"]].to_numpy()[i]
challenger_position = challenger.position[["easting", "northing"]].to_numpy()[i]
ego_velocity = ego.velocity[["easting", "northing"]].to_numpy()[i]
challenger_velocity = challenger.velocity[["easting", "northing"]].to_numpy()[i]
ego_length = ego.dimension.length.to_numpy()[i]
challenger_length = challenger.dimension.length.to_numpy()[i]

print(f"ego position: {ego_position},        velocity: {ego_velocity},   length: {ego_length} m")
print(f"challenger position: {challenger_position},   velocity: {challenger_velocity},   length: {challenger_length} m")

dp = challenger_position - ego_position
dv = challenger_velocity - ego_velocity
R = (ego_length + challenger_length) / 2

dp_dp = float(np.dot(dp, dp))
dp_dv = float(np.dot(dp, dv))
dv_dv = float(np.dot(dv, dv))

print(f"\ndp = {dp},   dv = {dv},   R = {R} m")
print(f"dp.dp = {dp_dp},   dp.dv = {dp_dv},   dv.dv = {dv_dv}")

a_coef = dv_dv
b_coef = 2 * dp_dv
c_coef = dp_dp - R**2
discriminant = b_coef**2 - 4 * a_coef * c_coef
root1 = (-b_coef + np.sqrt(discriminant)) / (2 * a_coef)
root2 = (-b_coef - np.sqrt(discriminant)) / (2 * a_coef)
ttc2d_by_hand = min(r for r in (root1, root2) if r >= 0)

print(f"\n{a_coef}*tau^2 + {b_coef}*tau + {c_coef} = 0")
print(f"discriminant = {b_coef}^2 - 4*{a_coef}*{c_coef} = {discriminant}")
print(f"roots: {root1:.4f}, {root2:.4f}  ->  smallest non-negative: {ttc2d_by_hand:.4f} s")
print(f"\nTTC2D.estimate(...) reports: {ttc2d.values[i]:.4f} s")

assert np.isclose(ttc2d_by_hand, ttc2d.values[i])
# %% [markdown]
# Matches exactly, as expected.
#
# ## Visualizing the interaction
# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(ego.position.easting, ego.position.northing, "o-", label="ego (eastbound)")
ax.plot(challenger.position.easting, challenger.position.northing, "s-", label="challenger (northbound)")
ax.plot(0, 0, "r*", markersize=15, label="predicted encounter point (t=3s)")
ax.set_xlabel("easting [m]")
ax.set_ylabel("northing [m]")
ax.legend()
ax.set_aspect("equal")
ax.set_title("Ego and challenger on a collision course")
