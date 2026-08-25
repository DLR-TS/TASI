import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Union

import numpy as np
import pandas as pd

from tasi.io import Position
from tasi.utils.geo import BasicGeometry, MultiGeometry, geometry_to_coords
from tasi.io.base import Base


class PETExtension(TrajectoryExtensionBase):

    def pet(
        self,
        other: Trajectory,
        reference: Tuple[str, str] = ("position", "position"),
        return_first: bool = True,
    ) -> PETResult | None:
        """
        Estimate the Post Encroachment Time (PET) between this trajectory and
        the other trajectory according to the reference point(s).

        Args:
            other (ObjectTrajectory): The other trajectory
            reference_point (Tuple[str, str]): Any of the pose reference points.
                                               Defaults to 'position'.

        Returns:
            PETResult: The PET between us and the other trajectory

        Notes:
            The PET is a signed value. A :math:`PET < 0` indicates that the
            current object crosses the intersection point after the other
            object.

        Raise:
            RuntimeError: If there is no intersection point between both
            trajectories.

        """
        if self.obj.equals(other):
            logging.info("Cannot estimate PET with ourself")
        else:
            return pet(self.obj, other, reference=reference, return_first=return_first)


class SMOSExtension(PETExtension):
    pass
