# %% [markdown]
# # Time Headway (THW)
#
# `THW` estimates, at every timestep of a car-following interaction, how many seconds it would take the
# following vehicle (`ego`), driving at its *current* speed, to reach the position the vehicle ahead of it
# (`challenger`) currently occupies. Unlike `TTC`, it is defined even when `ego` isn't closing in - it's a
# measure of following distance in time, not of an imminent collision.
#
# **Definition** (standard time-headway / traffic-flow safety indicator, e.g. Vogel, K. (2003), "A
# comparison of headway and time to collision as safety indicators," Accident Analysis & Prevention,
# 35(3), 427-433)::
#
#     gap(t)  = center-to-center distance - half the sum of both vehicles' lengths (net / bumper-to-bumper)
#     THW(t)  = gap(t) / ego.speed(t)               if ego.speed(t) > 0
#     THW(t)  = NaN                                 otherwise
#
# (Headway is sometimes defined "gross", front-bumper-to-front-bumper, instead - this implementation uses
# the net/bumper-to-bumper convention, matching the sibling `TTC`/`DRAC` metrics.)
#
# ## A plausible car-following interaction
#
# The same scenario as in the `TTC` example: `ego` drives at a constant 14 m/s (~50 km/h), 30 m behind
# `challenger`, who drives at a constant 10 m/s (~36 km/h). Both cars are 4.5 m long.
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
from tasi.smos import THW

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
# ## Computing THW
# %%
thw = THW.estimate(ego, challenger)
pd.Series(thw.values, index=thw.timestamps, name="THW [s]")
# %% [markdown]
# THW drops from about 1.8 s down to about 0.4 s - a headway well below the commonly cited 1-2 s "safe"
# threshold by the end of the window.
#
# ## Reproducing the value by hand
#
# Let's verify the value at `t=3s` (index 3) from the raw numbers `THW.estimate` used internally.
# %%
i = 3

ego_easting = ego.position.easting.to_numpy()[i]
challenger_easting = challenger.position.easting.to_numpy()[i]
ego_length = ego.dimension.length.to_numpy()[i]
challenger_length = challenger.dimension.length.to_numpy()[i]
ego_speed = ego.velocity.easting.to_numpy()[i]

print(f"ego position:         {ego_easting} m")
print(f"challenger position:  {challenger_easting} m")
print(f"ego length:           {ego_length} m")
print(f"challenger length:    {challenger_length} m")
print(f"ego speed:            {ego_speed} m/s")

gap = (challenger_easting - ego_easting) - (ego_length + challenger_length) / 2
thw_by_hand = gap / ego_speed

print(f"\ngap  = ({challenger_easting} - {ego_easting}) - ({ego_length} + {challenger_length}) / 2 = {gap} m")
print(f"THW  = {gap} / {ego_speed} = {thw_by_hand} s")
print(f"\nTHW.estimate(...) reports: {thw.values[i]} s")

assert np.isclose(thw_by_hand, thw.values[i])
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
