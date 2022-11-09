import numpy as np
import os
import torch
from PIL import Image
from torchvision import transforms
from model.ai.model.metaf import PoolFormer_test
from model.ai.utills.endecoder import crop_indexing, crop_aware_name_decoder, crop_aware_decoder_kr

BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Inference:

    meta_arg = {
        'name':'poolformer_m36',
        'model_name':PoolFormer_test,
        'path':"model/ai/weights/poolformer_nonpad.pth",
        'img_size':224,
    }
    
    """
    0:아무것도없음
    1:고추
    2:무
    3:배추
    4:애호박
    5:양배추
    6:오이
    7:토마토
    8:콩
    9:파
    10:호박
    """
    def __init__(self, device, crop:int):
        self.T = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize([0.485, 0.456, 0.406],[0.229, 0.224, 0.225])
                        ])
        # self.Resize =  transforms.Resize((img_size, img_size))
        self.crop = crop
        self.pad = True
        self.device = device
        self.m = False

    def get_model(self, model, name, pretrained=False):
        mdl = torch.nn.DataParallel(model(name)) if self.m else model(name)
        mdl.to(self.device)
        if not pretrained:
            return mdl
        else:
            print("기학습 웨이트")
            mdl.load_state_dict(torch.load(pretrained, map_location=self.device))
            return mdl
    
    def load_model(self):
        self.meta_model = self.get_model(model=Inference.meta_arg['model_name'], 
                                        name=Inference.meta_arg['name'],
                                        pretrained=Inference.meta_arg['path'])
    
    def predict(self, path:os.PathLike):
        img = Image.open(path).convert('RGB')
        if self.pad:
            img = expand2square(img)
        img = transforms.Resize((Inference.meta_arg['img_size'], Inference.meta_arg['img_size']))(img)
        img = self.T(img)
        self.meta_model.eval()
        with torch.no_grad():
            pred = self.meta_model(img[np.newaxis, ...]).detach().cpu().numpy()
            if self.crop == 0:
                pred_mask = np.argmax(pred, axis=-1)
            else:
                pred_mask = np.argmax(pred[...,crop_indexing[self.crop][0]:crop_indexing[self.crop][1]], axis=-1)+crop_aware_decoder_kr[str(self.crop).zfill(2)]
        return crop_aware_name_decoder[pred_mask[0]]

def expand2square(pil_img):
    background_color = (0,0,0)
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result
