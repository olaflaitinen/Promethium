import torch
import torch.nn as nn
import torch.autograd as autograd

class PhysicsInformedNN(nn.Module):
    """
    Physics-Informed Neural Network (PINN) for Acoustic Wave Equation.
    
    Minimizes: Loss = Loss_data + lambda * Loss_physics
    Where Loss_physics is the residual of the wave equation: u_tt - c^2 * (u_xx + u_zz) = 0
    """
    def __init__(self, layers=[3, 20, 20, 20, 20, 1]):
        super().__init__()
        self.depth = len(layers) - 1
        self.activation = nn.Tanh()
        
        layer_list = []
        for i in range(self.depth):
            layer_list.append(nn.Linear(layers[i], layers[i+1]))
        
        self.network = nn.ModuleList(layer_list)
        
        # Velocity model parameter (learnable or fixed)
        self.velocity = nn.Parameter(torch.tensor([2.0], requires_grad=True)) # e.g. 2 km/s

    def forward(self, x, z, t):
        # Input: spatial coordinates (x, z) and time (t)
        # Concatenate inputs
        X = torch.cat([x, z, t], dim=1)
        
        for i in range(self.depth - 1):
            X = self.activation(self.network[i](X))
        
        u = self.network[-1](X)
        return u

    def physics_loss(self, x, z, t):
        """
        Compute the residual of the acoustic wave equation.
        """
        # Ensure gradients are tracked
        x.requires_grad = True
        z.requires_grad = True
        t.requires_grad = True
        
        u = self.forward(x, z, t)
        
        # Compute derivatives
        u_t = autograd.grad(u, t, torch.ones_like(u), create_graph=True)[0]
        u_tt = autograd.grad(u_t, t, torch.ones_like(u_t), create_graph=True)[0]
        
        u_x = autograd.grad(u, x, torch.ones_like(u), create_graph=True)[0]
        u_xx = autograd.grad(u_x, x, torch.ones_like(u_x), create_graph=True)[0]
        
        u_z = autograd.grad(u, z, torch.ones_like(u), create_graph=True)[0]
        u_zz = autograd.grad(u_z, z, torch.ones_like(u_z), create_graph=True)[0]
        
        # Residual: u_tt - c^2 * (u_xx + u_zz)
        c2 = self.velocity ** 2
        residual = u_tt - c2 * (u_xx + u_zz)
        
        return torch.mean(residual ** 2)
