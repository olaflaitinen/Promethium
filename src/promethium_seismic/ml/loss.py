# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Loss functions for seismic reconstruction.

Three losses, in increasing order of what they assume about the data.
`PromethiumLoss` assumes nothing and is plain mean squared error.
`SpectralLoss` adds a penalty on the amplitude spectrum, because a
reconstruction can match sample by sample and still lose the frequency
content a geophysicist reads. `WaveEquationLoss` adds a physics residual and
assumes the wavefield obeys the scalar wave equation.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class PromethiumLoss(nn.Module):
    """Mean squared error between prediction and target."""

    def forward(self, pred, target):
        """Compute the loss.

        Args:
            pred: Predicted wavefield.
            target: Reference wavefield.

        Returns:
            A scalar tensor.
        """
        return F.mse_loss(pred, target)


class SpectralLoss(PromethiumLoss):
    """Mean squared error plus a penalty on the amplitude spectrum.

    Seismic interpretation reads frequency content, and a reconstruction can
    match closely sample by sample while smoothing the spectrum. The spectral
    term makes that visible to the optimiser.
    """

    def __init__(self, alpha=1.0):
        """Build the loss.

        Args:
            alpha: Weight on the spectral term relative to the sample term.
        """
        super().__init__()
        self.alpha = alpha

    def forward(self, pred, target):
        """Compute the loss.

        Args:
            pred: Predicted wavefield.
            target: Reference wavefield.

        Returns:
            A scalar tensor.
        """
        mse = F.mse_loss(pred, target)

        # Real valued input, so the one sided transform carries everything.
        pred_fft = torch.fft.rfft2(pred)
        target_fft = torch.fft.rfft2(target)

        spectral_mse = F.mse_loss(torch.abs(pred_fft), torch.abs(target_fft))

        return mse + self.alpha * spectral_mse


def _second_difference(field: torch.Tensor, dim: int, spacing: float) -> torch.Tensor:
    """Second derivative along one axis by central differences.

    Args:
        field: The wavefield.
        dim: The axis to differentiate along.
        spacing: The sample interval along that axis.

    Returns:
        The second derivative, two samples shorter along `dim` because the
        stencil needs a neighbour on each side.
    """
    forward = field.narrow(dim, 2, field.size(dim) - 2)
    centre = field.narrow(dim, 1, field.size(dim) - 2)
    backward = field.narrow(dim, 0, field.size(dim) - 2)
    return (forward - 2.0 * centre + backward) / (spacing * spacing)


class WaveEquationLoss(PromethiumLoss):
    """Mean squared error plus a scalar wave equation residual.

    The residual is

        r = u_tt - c^2 * u_xx

    evaluated by central differences on the interior of the patch. The loss
    is the data term plus `beta` times the mean square of `r`.

    Input is expected as (batch, channel, time, space), which is what the
    models in this package produce. That is one spatial axis, so the equation
    enforced is the one dimensional one. This docstring used to promise
    `u_xx + u_zz`; with a single spatial axis there is no second spatial
    derivative to take, and claiming otherwise would describe an equation
    this code cannot evaluate.

    **On scaling.** The residual carries physical units and its size depends
    on the grid. With the defaults, `1 / dt^2` is 1e6 while `c^2 / dx^2` is
    2.25e4, so on amplitude normalised data the physics term dwarfs the data
    term unless `beta` is very small. Passing `normalize=True` divides the
    residual by the root mean square of `u_tt`, which makes it dimensionless
    and makes `beta` mean the same thing from one grid to the next. It is off
    by default because it changes the quantity being minimised.
    """

    def __init__(self, c=1500.0, dt=0.001, dx=10.0, dz=10.0, beta=0.1, normalize=False):
        """Build the loss.

        Args:
            c: Wave speed in metres per second. A float, or a tensor
                broadcastable against the residual for a velocity model.
            dt: Time sample interval in seconds.
            dx: Spatial sample interval in metres.
            dz: Depth sample interval in metres. Accepted so that a caller
                can pass a full grid description, and unused while the input
                carries one spatial axis.
            beta: Weight on the physics term relative to the data term.
            normalize: Divide the residual by the root mean square of the
                time curvature, making the physics term dimensionless.
        """
        super().__init__()
        self.c = c
        self.dt = dt
        self.dx = dx
        self.dz = dz
        self.beta = beta
        self.normalize = normalize

    def physics_residual(self, field: torch.Tensor) -> torch.Tensor:
        """Evaluate the wave equation residual on the interior of a patch.

        Args:
            field: Wavefield as (batch, channel, time, space).

        Returns:
            The residual, two samples shorter along each differentiated axis.

        Raises:
            ValueError: if the input is not four dimensional, or if the patch
                is smaller than the three samples a central difference needs.
        """
        if field.ndim != 4:
            raise ValueError(
                f"expected (batch, channel, time, space), got {tuple(field.shape)}"
            )
        if field.size(2) < 3 or field.size(3) < 3:
            raise ValueError(
                "the central difference stencil needs at least three samples "
                f"along time and space, got {field.size(2)} and {field.size(3)}"
            )

        u_tt = _second_difference(field, dim=2, spacing=self.dt)
        u_xx = _second_difference(field, dim=3, spacing=self.dx)

        # Each derivative loses a sample at both ends of its own axis, so the
        # two only line up on the interior of both.
        u_tt = u_tt.narrow(3, 1, u_tt.size(3) - 2)
        u_xx = u_xx.narrow(2, 1, u_xx.size(2) - 2)

        speed = self.c
        if not torch.is_tensor(speed):
            speed = torch.as_tensor(speed, dtype=field.dtype, device=field.device)

        residual = u_tt - (speed**2) * u_xx

        if self.normalize:
            scale = torch.sqrt(torch.mean(u_tt**2)) + torch.finfo(field.dtype).eps
            residual = residual / scale

        return residual

    def forward(self, pred, target):
        """Compute the loss.

        Args:
            pred: Predicted wavefield as (batch, channel, time, space).
            target: Reference wavefield of the same shape.

        Returns:
            A scalar tensor: the data term plus `beta` times the mean square
            residual.
        """
        mse = F.mse_loss(pred, target)
        residual = self.physics_residual(pred)
        return mse + self.beta * torch.mean(residual**2)
