import logging
from typing import Tuple

from tasi import Trajectory
from tasi.smos.pet import PET

from ..base import TrajectoryExtensionBase


class PETExtension(TrajectoryExtensionBase):

    def pet(
        self,
        other: Trajectory,
        position: Tuple[Tuple[str, ...] | str, Tuple[str, ...] | str] = (
            ("boundingbox", "center"),
            ("boundingbox", "center"),
        ),
        return_first: bool = True,
    ) -> PET | None:
        """
        Estimate the Post Encroachment Time (PET) between this trajectory and
        the `other` trajectory according to the reference point(s).

        Args:
            other (ObjectTrajectory): The other trajectory
            reference_point (Tuple[str, str]): Any of the pose 'position' points.
                                               Defaults to 'center' position.

        Returns:
            PET: The PET between us and the other trajectory. None if
            trying to estimate the PET with itself.

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
            return PET.estimate(
                self.obj, other, position=position, return_first=return_first
            )
