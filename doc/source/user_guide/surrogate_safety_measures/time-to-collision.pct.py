# %% [markdown]
# # Time-to-Collision (TTC)
#
# `TTC` estimates, at every timestep of a car-following interaction, how many seconds remain until a
# closing-in following vehicle (`ego`) would collide with the vehicle ahead of it (`challenger`), if both
# continued at their current speed. The smaller the value, the more urgent the situation.
#
# **Definition** (Hayward, J.C. (1972), "Near miss determination through use of a scale of danger,"
# Highway Research Record, 384, 24-34)::
#
#     gap(t)           = center-to-center distance - half the sum of both vehicles' lengths (bumper-to-bumper)
#     closing_speed(t)  = ego.speed(t) - challenger.speed(t)
#     TTC(t)            = gap(t) / closing_speed(t)          if closing_speed(t) > 0
#     TTC(t)            = NaN                                otherwise (not closing in)
#
# ## A plausible car-following interaction
#
# To keep the numbers easy to follow by hand, we construct a small synthetic scenario instead of using a
# real recording: a car (`ego`) is driving at 14 m/s (~50 km/h) 30 m behind another car (`challenger`)
# that drives at a constant 10 m/s (~36 km/h) - a plausible closing car-following situation. Both cars are
# 4.5 m long.
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
from tasi.smos import TTC

T0 = datetime(2024, 1, 1, 12, 0, 0)
DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)
CLASSIFICATIONS = Classifications(car=1.0)


def make_trajectory(id_object, origin, velocity, n_steps=6, dt=1.0):
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


ego = make_trajectory(id_object=1, origin=(0.0, 0.0), velocity=(14.0, 0.0))
challenger = make_trajectory(id_object=2, origin=(30.0, 0.0), velocity=(10.0, 0.0))

ego.position.easting
# %% [markdown]
# ## Computing TTC
# %%
ttc = TTC.estimate(ego, challenger)
pd.Series(ttc.values, index=ttc.timestamps, name="TTC [s]")
# %% [markdown]
# TTC drops from about 6.4 s down to about 1.4 s as the gap closes - exactly the kind of decreasing trend
# a real approaching, unresolved conflict would show.
#
# ## Reproducing the value by hand
#
# Let's verify the value at `t=3s` (index 3) from the raw numbers `TTC.estimate` used internally, so it's
# clear the function's output is exactly what the formula above predicts.
# %%
i = 3

ego_easting = ego.position.easting.to_numpy()[i]
challenger_easting = challenger.position.easting.to_numpy()[i]
ego_length = ego.dimension.length.to_numpy()[i]
challenger_length = challenger.dimension.length.to_numpy()[i]
ego_speed = ego.velocity.easting.to_numpy()[i]
challenger_speed = challenger.velocity.easting.to_numpy()[i]

print(f"ego position:         {ego_easting} m")
print(f"challenger position:  {challenger_easting} m")
print(f"ego length:           {ego_length} m")
print(f"challenger length:    {challenger_length} m")
print(f"ego speed:            {ego_speed} m/s")
print(f"challenger speed:     {challenger_speed} m/s")

gap = (challenger_easting - ego_easting) - (ego_length + challenger_length) / 2
closing_speed = ego_speed - challenger_speed
ttc_by_hand = gap / closing_speed

print(f"\ngap            = ({challenger_easting} - {ego_easting}) - ({ego_length} + {challenger_length}) / 2 = {gap} m")
print(f"closing_speed  = {ego_speed} - {challenger_speed} = {closing_speed} m/s")
print(f"TTC            = {gap} / {closing_speed} = {ttc_by_hand} s")
print(f"\nTTC.estimate(...) reports: {ttc.values[i]} s")

assert np.isclose(ttc_by_hand, ttc.values[i])
# %% [markdown]
# Matches exactly, as expected.
#
# ## Visualizing the interaction
# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(ego.position.easting, [0] * len(ego), "o-", label="ego (following)")
ax.plot(challenger.position.easting, [0] * len(challenger), "s-", label="challenger (leading)")
ax.set_xlabel("easting [m]")
ax.set_yticks([])
ax.legend()
ax.set_title("Ego closing in on challenger")
