# %% [markdown]
# # Time Advantage (TAdv)
#
# `TAdv` estimates, at every timestep of an interaction where two paths cross, how much time margin exists
# between the two participants *if* both kept their current position, speed and heading unchanged: the
# absolute difference between the time each of them would still need to reach the (fixed) point where
# their paths cross. Unlike `PET` (which looks at *actual* arrival times after the fact), `TAdv` can be
# evaluated continuously, before either participant has actually reached the conflict point.
#
# **Definition** (commonly attributed to Hansson, K.G. (1975), and used throughout the Swedish Traffic
# Conflict Technique tradition, e.g. Hydén, C. (1987), "The development of a method for traffic safety
# evaluation: The Swedish traffic conflict technique," Lund University doctoral thesis)::
#
#     TAdv(t) = | d_ego(t) / v_ego(t)  -  d_challenger(t) / v_challenger(t) |
#
# where `d_ego(t)` / `d_challenger(t)` is each participant's straight-line distance from its position at
# `t` to the (static) conflict point, and `v_ego(t)` / `v_challenger(t)` is each participant's
# instantaneous speed.
#
# ## A plausible crossing interaction
#
# Two cars approach the same point from different directions, like at an unsignalized intersection: `ego`
# drives east at 12 m/s (~43 km/h) starting 36 m west of the crossing point; `challenger` drives north at
# 10 m/s (~36 km/h) starting 24 m south of it. Both would reach the crossing point *before* they'd collide
# with each other (ego at `t=3s`, challenger already at `t=2.4s`) - a routine, resolved crossing, not a
# near-miss.
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
from tasi.smos import TAdv

T0 = datetime(2024, 1, 1, 12, 0, 0)
DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)
CLASSIFICATIONS = Classifications(car=1.0)


def make_trajectory(id_object, origin, velocity, n_steps=8, dt=0.5):
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
challenger = make_trajectory(id_object=2, origin=(0.0, -24.0), velocity=(0.0, 10.0))

ego.position[["easting", "northing"]]
# %% [markdown]
# ## Computing TAdv
# %%
tadv = TAdv.estimate(ego, challenger)
pd.Series(tadv.values, index=tadv.timestamps, name="TAdv [s]")
# %% [markdown]
# While both participants are still approaching (`t=0` to `t=2.0`), TAdv is a *constant* 0.6 s. That's not
# a coincidence: for a participant moving at constant velocity straight toward the point, `distance(t) /
# speed(t)` equals `arrival_time - t` - a straight line in `t` with slope `-1`. Subtracting the two just
# leaves the constant difference between their (unchanged) arrival times, `3.0 s - 2.4 s = 0.6 s`.
#
# At `t=2.5s` the value briefly dips to 0.4 s - right after `challenger` has *already passed* the conflict
# point (at `t=2.4s`). `distance(t)` is a plain (always non-negative) Euclidean distance, so once a
# participant has passed the point it no longer distinguishes "still approaching" from "just left" - a
# real limitation of this formula worth being aware of when interpreting TAdv near or after either
# participant's crossing.
#
# ## Reproducing the value by hand
#
# Let's verify the value at `t=0s` (index 0) from the raw numbers `TAdv.estimate` used internally.
# %%
from tasi.smos.geometry import conflict_point

i = 0

result = conflict_point(ego, challenger)
point, _, _ = result
print(f"conflict point: {point}")

ego_position = ego.position[["easting", "northing"]].to_numpy()[i]
challenger_position = challenger.position[["easting", "northing"]].to_numpy()[i]
ego_velocity = ego.velocity[["easting", "northing"]].to_numpy()[i]
challenger_velocity = challenger.velocity[["easting", "northing"]].to_numpy()[i]

d_ego = np.linalg.norm(point - ego_position)
d_challenger = np.linalg.norm(point - challenger_position)
v_ego = np.linalg.norm(ego_velocity)
v_challenger = np.linalg.norm(challenger_velocity)

print(f"\nego position: {ego_position},   distance to conflict point: {d_ego} m,   speed: {v_ego} m/s")
print(f"challenger position: {challenger_position},   distance to conflict point: {d_challenger} m,   speed: {v_challenger} m/s")

t_ego = d_ego / v_ego
t_challenger = d_challenger / v_challenger
tadv_by_hand = abs(t_ego - t_challenger)

print(f"\nt_ego         = {d_ego} / {v_ego} = {t_ego} s")
print(f"t_challenger  = {d_challenger} / {v_challenger} = {t_challenger} s")
print(f"TAdv          = |{t_ego} - {t_challenger}| = {tadv_by_hand} s")
print(f"\nTAdv.estimate(...) reports: {tadv.values[i]} s")

assert np.isclose(tadv_by_hand, tadv.values[i])
# %% [markdown]
# Matches exactly, as expected.
#
# ## Visualizing the interaction
# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(ego.position.easting, ego.position.northing, "o-", label="ego (eastbound)")
ax.plot(challenger.position.easting, challenger.position.northing, "s-", label="challenger (northbound)")
ax.plot(*point, "r*", markersize=15, label="conflict point")
ax.set_xlabel("easting [m]")
ax.set_ylabel("northing [m]")
ax.legend()
ax.set_aspect("equal")
ax.set_title("Ego and challenger crossing at an intersection")
