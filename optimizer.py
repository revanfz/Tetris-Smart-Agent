import torch
import torch.optim as optim

class SharedAdam(optim.Adam):
    """
    Inisialisasi Global Shared Optimizer
    """

    def __init__(
        self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0
    ) -> None:
        super(SharedAdam, self).__init__(
            params, lr=lr, betas=betas, eps=eps, weight_decay=weight_decay
        )

        for group in self.param_groups:
            for p in group["params"]:
                state = self.state[p]
                state["step"] = torch.zeros(1)
                state["exp_avg"] = torch.zeros_like(p.data)
                state["exp_avg_sq"] = torch.zeros_like(p.data)

                state["exp_avg"].share_memory_()
                state["exp_avg_sq"].share_memory_()
