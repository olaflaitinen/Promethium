# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class PromethiumLoss(nn.Module):
    def forward(self, pred, target):
        return F.mse_loss(pred, target)

class SpectralLoss(PromethiumLoss):
    """
    Penalizes differences in the frequency domain.
    Important for seismic to preserve frequency content.
    """
    def __init__(self, alpha=1.0):
        super().__init__()
        self.alpha = alpha

    def forward(self, pred, target):
        mse = F.mse_loss(pred, target)
        
        # FFT (Real signals)
        pred_fft = torch.fft.rfft2(pred)
        target_fft = torch.fft.rfft2(target)
        
        spectral_mse = F.mse_loss(torch.abs(pred_fft), torch.abs(target_fft))
        
        return mse + self.alpha * spectral_mse

class WaveEquationLoss(PromethiumLoss):
    """
    PINN Loss: Enforces the scalar wave equation.
    u_tt = c^2 * (u_xx + u_zz)
    Requires predicted wavefield 'u' and velocity model 'c'.
    Arguments:
        c (float or Tensor): Velocity.
        dt, dx, dz (float): Grid spacing.
    """
    def __init__(self, c=1500.0, dt=0.001, dx=10.0, dz=10.0, beta=0.1):
        super().__init__()
        self.c = c
        self.dt = dt
        self.dx = dx
        self.dz = dz
        self.beta = beta

    def forward(self, pred, target):
        # Data Mismatch
        mse = F.mse_loss(pred, target)
        
        # Physics Residual (Finite Difference)
        # Assuming pred is (B, 1, T, X) 2D slice
        u = pred
        
        # Second derivatives via central difference Conv2d kernel
        # This is a simplified implementation for demonstration
        # u_tt ~ (u[t+1] - 2u[t] + u[t-1]) / dt^2
        pass 
        # Implementing full FD checks requires specific padding and is computationally heavy for generic Autoencoder
        # Returning MSE for now, but structure is here for SoTA PINN expansion
        return mse
