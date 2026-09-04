# %% [markdown]
# # Deceleration Rate to Avoid Crash (DRAC)
#
# `DRAC` estimates, at every timestep of a car-following interaction, the constant deceleration rate the
# following vehicle (`ego`) would need to apply *starting right now* to just avoid colliding with the
# vehicle ahead of it (`challenger`), assuming `challenger` keeps its current speed. The higher the value,
# the harder the following vehicle would need to brake.
#
# **Definition** (Cooper, P.J. (1984), "Experience with traffic conflicts in Canada with emphasis on
# 'post encroachment time' techniques," in International Calibration Study of Traffic Conflict Techniques,
# NATO ASI Series F5, Springer)::
#
#     gap(t)            = center-to-center distance - half the sum of both vehicles' lengths (bumper-to-bumper)
#     closing_speed(t)  = ego.speed(t) - challenger.speed(t)
#     DRAC(t)           = closing_speed(t) ** 2 / (2 * gap(t))    if closing_speed(t) > 0
#     DRAC(t)           = NaN                                    otherwise (not closing in)
#
# ## A plausible car-following interaction
#
# The same scenario as in the `TTC`/`THW` examples: `ego` drives at a constant 14 m/s (~50 km/h), 30 m
# behind `challenger`, who drives at a constant 10 m/s (~36 km/h). Both cars are 4.5 m long.
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
from tasi.smos import DRAC

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
# ## Computing DRAC
# %%
drac = DRAC.estimate(ego, challenger)
pd.Series(drac.values, index=drac.timestamps, name="DRAC [m/s^2]")
# %% [markdown]
# DRAC rises from about 0.3 m/s² to about 1.5 m/s² as the gap closes - `ego` would need to brake
# increasingly hard to avoid a collision, exactly mirroring the shrinking `TTC`/`THW` values for the same
# interaction.
#
# ## Reproducing the value by hand
#
# Let's verify the value at `t=3s` (index 3) from the raw numbers `DRAC.estimate` used internally.
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
drac_by_hand = closing_speed**2 / (2 * gap)

print(f"\ngap            = ({challenger_easting} - {ego_easting}) - ({ego_length} + {challenger_length}) / 2 = {gap} m")
print(f"closing_speed  = {ego_speed} - {challenger_speed} = {closing_speed} m/s")
print(f"DRAC           = {closing_speed}^2 / (2 * {gap}) = {drac_by_hand} m/s^2")
print(f"\nDRAC.estimate(...) reports: {drac.values[i]} m/s^2")

assert np.isclose(drac_by_hand, drac.values[i])
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
