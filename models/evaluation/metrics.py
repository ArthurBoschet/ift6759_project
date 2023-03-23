import torch.nn as nn
import torch


class Loss_Custom(nn.Module):
    def __init__(self,list_loss:nn.ModuleList,list_pond: list):
        '''

        Parameters
        ----------
        list_loss : list of different loss to mesure
        list_pond : list of ponderations of different loss in list loss
        '''
        super(Loss_Custom, self).__init__()
        self.list_loss = list_loss
        self.list_pond = list_pond

    def forward(self,predict,target):
        cumul_loss = 0
        for i,loss in enumerate(self.list_loss):
            cumul_loss += self.list_pond[i] * loss(predict,target)
        return cumul_loss
        


class Dice_Loss(nn.Module):
    def __init__(self, smooth: float = 1e-7,log_loss=False):
        '''
        Dice loss implementation for multiclasses segmentation purposes

        https://github.com/BloodAxe/pytorch-toolbelt/blob/develop/pytorch_toolbelt/losses/functional.py
        '''

        super(Dice_Loss, self).__init__()
        self.smooth = smooth
        self.log_loss = log_loss

    def forward(self,pred,target):
        '''

        Parameters
        ----------
        pred (torch.Tensor) : tensors which contains prediction (N,NC,D,H,W)
        target (torch.Tensor): tensor which contains actual labels (N,D,H,W)
        N = batch size , NC = number of classes, D= depth , H = height, W = width

        Returns

        dice score loss (float): loss value for dice score
        -------
        '''

        # get dimensions of samples
        batch_size = pred.shape[0]
        n_class = pred.shape[1]

        # we get one hot encoding of target prediction
        target = nn.functional.one_hot(target, n_class)
        # we permute to get same shape as prediction tensor
        target = torch.permute(target, (0,4,1,2,3))

        # check if pred size and target size are a match
        assert pred.shape == target.shape

        # logits to probability for prediction
        pred = nn.functional.softmax(pred,dim=1)

        # we switch to flatten version of vectors
        pred = pred.view(batch_size, n_class, -1)
        target = target.view(batch_size,n_class,-1)

        # calculate multi-class dice loss
        inter = torch.sum(pred*target)
        card  = torch.sum(pred+target)
        dice_score = 2*(inter+self.smooth)/(card+self.smooth)
        loss =  1 - dice_score if not self.log_loss else -torch.log(dice_score)
        return loss

class CrossEntropy(nn.Module):
    '''

    '''
    def __init__(self,label_smoothing= 0.0):
        super(CrossEntropy, self).__init__()
        self.criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)

    def forward(self,pred,target):
        '''

        Parameters
        ----------
        pred (torch.Tensor) : tensors which contains prediction (N,D,H,W)
        target (torch.Tensor): tensor which contains actual labels (N,D,H,W)

        Returns
        -------
        loss (float): CE loss value
        '''

        return self.criterion(pred,target)

def iou_pytorch(pred_mask, target_mask):
    assert pred_mask.shape == target_mask.shape, "Shape mismatch in input masks."

    # Make sure the input tensors are boolean
    pred_mask = pred_mask.bool()
    target_mask = target_mask.bool()

    # Calculate intersection
    intersection = (pred_mask & target_mask).float().sum()

    # Calculate union
    union = (pred_mask | target_mask).float().sum()

    # Calculate IoU
    iou = intersection / (union + 1e-6)  # Adding a small epsilon to avoid division by zero

    return iou
