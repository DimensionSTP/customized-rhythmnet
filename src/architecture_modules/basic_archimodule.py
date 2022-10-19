import math

from torch import nn, optim
from torch.nn import functional as F

from pytorch_lightning import LightningModule


class RbpmPlModule(LightningModule):
    def __init__(
        self, model: nn.Module, lr: float, t_max: int, eta_min: float, interval: str
    ):
        super().__init__()
        self.model = model
        self.lr = lr
        self.t_max = t_max
        self.eta_min = eta_min
        self.interval = interval

    def forward(self, stmap):
        _, output = self.model(stmap)
        return output

    def step(self, batch):
        stmap, label = batch
        pred = self(stmap)
        loss = F.mse_loss(pred, label)
        visual_loss = F.l1_loss(pred, label)
        return loss, pred, label, visual_loss

    def configure_optimizers(self):
        adam_w_optimizer = optim.AdamW(self.parameters(), lr=self.lr)
        cosine_scheduler = optim.lr_scheduler.CosineAnnealingLR(
            adam_w_optimizer, T_max=self.t_max, eta_min=self.eta_min
        )
        return {
            "optimizer": adam_w_optimizer,
            "lr_scheduler": {"scheduler": cosine_scheduler, "interval": self.interval},
        }

    def training_step(self, batch, batch_idx):
        loss, pred, label, visual_loss = self.step(batch)
        self.log(
            "train_rmse_loss",
            math.sqrt(loss),
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )
        self.log(
            "train_mae_loss",
            visual_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )
        return loss

    def validation_step(self, batch, batch_idx):
        loss, pred, label, visual_loss = self.step(batch)
        self.log(
            "val_rmse_loss",
            math.sqrt(loss),
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )
        self.log(
            "val_mae_loss",
            visual_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )
        return loss

    def test_step(self, batch, batch_idx):
        loss, pred, label, visual_loss = self.step(batch)
        self.log(
            "test_rmse_loss",
            math.sqrt(loss),
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )
        self.log(
            "test_mae_loss",
            visual_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            rank_zero_only=True,
            sync_dist=False,
        )