import torch
import torch.nn as nn
import torch.nn.functional as F

#kernel size
k_size = 3

###########################################################################

class BuildingBlock(nn.Module):

    def __init__(self, ch_in, ch_out, downsample):
        '''
        downsample = Boolean
        '''
        super(BuildingBlock, self).__init__()
        self.first_stride = 2 if downsample else 1
        self.first = nn.Conv2d(ch_in, ch_out, k_size, stride=self.first_stride)
        self.second = nn.Conv2d(ch_out, ch_out, k_size)
        self.batch = nn.BatchNorm2d(ch_out)
        self.downsample = downsample
        self.down = nn.Conv2d(ch_in, ch_out, 1, stride=2)
        

    def forward(self, x):
        #First layer
        x_res = x
        x = self.batch(self.first(x))
        x = F.relu(x)
        
        #Second layer
        x = self.batch(self.second(x))
        
        if self.downsample:
            x_res = self.batch(self.down(x))
        
        x += x_res
        x = F.relu(self.batch(x))
        
        return x
        
###########################################################################

class BottelneckBlock(nn.Module):
    def __init__(self, ch_in, ch_out, ch_midd, downsample):
        '''
        downsample = Boolean
        '''
        super(BottelneckBlock, self).__init__()
        self.first_stride = 2 if downsample else 1
        self.first = nn.Conv2d(ch_in, ch_midd, 1, stride=first_stride)
        self.second = nn.Conv2d(ch_midd, ch_midd, k_size)
        self.third = nn.Conv2d(ch_midd, ch_out, 1)
        self.batch1 = nn.BatchNorm2d(ch_midd)
        self.batch2 = nn.BatchNorm2d(ch_out)
        self.downsample = downsample
        self.down = nn.Conv2d(ch_in, ch_out, 1, stride=2)

    def forward(self, x):
        #First layer
        x_res = x
        x = self.batch1(self.first(x))
        x = F.relu(x)
        
        #Second layer
        x = self.batch1(self.second(x))
        x = F.relu(x)
        
        #Third layer
        x = self.batch2(self.third(x))
        
        if self.downsample:
            x_res = self.batch2(self.down(x))
        
        x += x_res
        x = F.relu(self.batch2(x))
        
        return x
        
###########################################################################

#This class is a sequence of blocks of same size. Only the first block is with downsample.
class BlockSequence(nn.Module):
    def __init__(self, ch_in, ch_out, num_block):
        super(BlockSequence, self).__init__()
        
        self.seq_block = nn.Sequential(*[BuildingBlock(ch_in, ch_out, True) if i == 0 //
                                         else BuildingBlock(ch_in, ch_out, False) for i in range(num_block)])
        
    def forward(self, x):
        x = self.seq_block(x)
        return x
        
###########################################################################

#This class is a sequence of blocks of same size. Only the first block is with downsample.
class BottelneckSequence(nn.Module):
    def __init__(self, ch_in, ch_midd, ch_out, num_block):
        super(BottelneckSequence, self).__init__()
        
        self.seq_block = nn.Sequential(*[BottelneckBlock(ch_in, ch_midd, ch_out, True) if i == 0 //
                                         else BottelneckBlock(ch_in, ch_midd, ch_out, False) for i in range(num_block)])
        
    def forward(self, x):
        x = self.seq_block(x)
        return x
        
###########################################################################
        
class ResNet(nn.Module):
    def __init__(self, ch_in, ch_size, num_block):
        super(BlockSequence, self).__init__()
        self.conv = nn.Conv2d(ch_in, ch_size, 7,stride=2)
        self.pool = nn.MaxPool2d(3, stride=2)
        
        #here goes stack of sequence block. This depends on the architecture


        self.avgpool = nn.AvgPool2d(3)
        self.fc = nn.Linear()
