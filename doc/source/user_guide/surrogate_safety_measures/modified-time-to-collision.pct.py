# %% [markdown]
# # Modified Time-to-Collision (MTTC)
#
# `MTTC` generalizes `TTC` to also account for a *difference in acceleration* between the two vehicles,
# instead of assuming both keep a constant speed. This matters whenever one vehicle is actively speeding
# up or braking relative to the other - a plain `TTC` snapshot would miss that.
#
# **Definition** (Ozbay, K., Yang, H., & Bartin, B. (2008), "Derivation and validation of new
# simulation-based surrogate safety measure," Transportation Research Record, 2083(1), 105-113): let, at
# time `t`, `gap(t)` be the bumper-to-bumper distance, `dv(t) = ego.speed(t) - challenger.speed(t)` the
# closing speed, and `da(t) = ego.accel(t) - challenger.accel(t)` the relative acceleration. Projecting the
# gap forward by `tau` seconds under constant acceleration::
#
#     gap(t + tau) = gap(t) - dv(t) * tau - 0.5 * da(t) * tau ** 2
#
# `MTTC(t)` is the smallest non-negative real root `tau` of `0.5 * da(t) * tau ** 2 + dv(t) * tau - gap(t)
# = 0`. When `da(t)` is (numerically) zero this reduces to the classic `TTC = gap(t) / dv(t)`.
#
# ## A plausible car-following interaction with acceleration
#
# `ego` starts at 14 m/s and *accelerates* at 1 m/s² (e.g. impatiently closing a gap), 30 m behind
# `challenger`, who drives at a constant 10 m/s (no acceleration). Both cars are 4.5 m long. Unlike the
# `TTC`/`THW`/`DRAC` examples (which reuse a plain constant-velocity scenario), this one needs a
# non-zero relative acceleration to actually exercise MTTC's quadratic term.
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
from tasi.smos import MTTC

T0 = datetime(2024, 1, 1, 12, 0, 0)
DIMENSION = Dimension(width=1.8, height=1.5, length=4.5)
CLASSIFICATIONS = Classifications(car=1.0)


def make_accelerating_trajectory(id_object, origin, v0, accel, n_steps=4, dt=1.0):
    """Build a straight `Trajectory` for a car of `DIMENSION` with constant acceleration `accel`."""
    tp = TrafficParticipant(id_object=id_object, classifications=CLASSIFICATIONS, dimension=DIMENSION)
    poses = []
    for i in range(n_steps):
        t = i * dt
        easting = origin + v0 * t + 0.5 * accel * t**2
        speed = v0 + accel * t
        position = Position(easting=easting, northing=0.0)
        poses.append(
            PosePublic(
                timestamp=T0 + timedelta(seconds=t),
                position=position,
                orientation=0.0,
                traffic_participant=tp,
                dimension=DIMENSION,
                velocity=Velocity(x=speed, y=0.0),
                acceleration=Acceleration(x=accel, y=0.0),
                classifications=CLASSIFICATIONS,
                boundingbox=BoundingBox.from_dimension(DIMENSION, relative_to=position),
            )
        )
    return TrajectoryPublic(poses=poses, traffic_participant=tp).as_tasi()


ego = make_accelerating_trajectory(id_object=1, origin=0.0, v0=14.0, accel=1.0)
challenger = make_accelerating_trajectory(id_object=2, origin=30.0, v0=10.0, accel=0.0)

ego.position.easting
# %% [markdown]
# ## Computing MTTC
# %%
mttc = MTTC.estimate(ego, challenger)
pd.Series(mttc.values, index=mttc.timestamps, name="MTTC [s]")
# %% [markdown]
# ## Reproducing the value by hand
#
# Let's verify the value at `t=1s` (index 1), where the relative acceleration is genuinely non-zero, so
# the quadratic term actually matters (not just the plain `TTC` fallback).
# %%
i = 1

ego_easting = ego.position.easting.to_numpy()[i]
challenger_easting = challenger.position.easting.to_numpy()[i]
ego_length = ego.dimension.length.to_numpy()[i]
challenger_length = challenger.dimension.length.to_numpy()[i]
ego_speed = ego.velocity.easting.to_numpy()[i]
challenger_speed = challenger.velocity.easting.to_numpy()[i]
ego_accel = ego.acceleration.easting.to_numpy()[i]
challenger_accel = challenger.acceleration.easting.to_numpy()[i]

print(f"ego position:      {ego_easting} m,   speed: {ego_speed} m/s,   accel: {ego_accel} m/s^2")
print(f"challenger position: {challenger_easting} m,   speed: {challenger_speed} m/s,   accel: {challenger_accel} m/s^2")

gap = (challenger_easting - ego_easting) - (ego_length + challenger_length) / 2
dv = ego_speed - challenger_speed
da = ego_accel - challenger_accel

print(f"\ngap = ({challenger_easting} - {ego_easting}) - {(ego_length + challenger_length) / 2} = {gap} m")
print(f"dv  = {ego_speed} - {challenger_speed} = {dv} m/s")
print(f"da  = {ego_accel} - {challenger_accel} = {da} m/s^2")

# solve 0.5 * da * tau**2 + dv * tau - gap = 0
a_coef = 0.5 * da
b_coef = dv
c_coef = -gap
discriminant = b_coef**2 - 4 * a_coef * c_coef
root1 = (-b_coef + np.sqrt(discriminant)) / (2 * a_coef)
root2 = (-b_coef - np.sqrt(discriminant)) / (2 * a_coef)
mttc_by_hand = min(r for r in (root1, root2) if r >= 0)

print(f"\n0.5*{da}*tau^2 + {dv}*tau - {gap} = 0")
print(f"discriminant = {b_coef}^2 - 4*{a_coef}*{c_coef} = {discriminant}")
print(f"roots: {root1:.4f}, {root2:.4f}  ->  smallest non-negative: {mttc_by_hand:.4f} s")
print(f"\nMTTC.estimate(...) reports: {mttc.values[i]:.4f} s")

assert np.isclose(mttc_by_hand, mttc.values[i])
# %% [markdown]
# Matches exactly, as expected. It's also instructive to compare this against what the plain,
# constant-velocity `TTC` formula (`gap / dv`) would have predicted at the same instant, ignoring that
# `ego` keeps accelerating:
# %%
plain_ttc = gap / dv
print(f"plain TTC (ignoring acceleration):  {gap} / {dv} = {plain_ttc:.4f} s")
print(f"MTTC (accounting for acceleration): {mttc_by_hand:.4f} s")
# %% [markdown]
# MTTC is shorter than the plain-TTC estimate: because `ego` keeps accelerating, the gap actually closes
# *sooner* than a constant-velocity projection would suggest.
# %% [markdown]
# ## Visualizing the interaction
# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(ego.position.easting, [0] * len(ego), "o-", label="ego (following, accelerating)")
ax.plot(challenger.position.easting, [0] * len(challenger), "s-", label="challenger (leading, constant speed)")
ax.set_xlabel("easting [m]")
ax.set_yticks([])
ax.legend()
ax.set_title("Ego closing in on challenger while accelerating")
