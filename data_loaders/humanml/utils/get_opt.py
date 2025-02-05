import os
from argparse import Namespace
import re
from os.path import join as pjoin
from data_loaders.humanml.utils.word_vectorizer import POS_enumerator
from pprint import pprint


def is_float(numStr):
    flag = False
    numStr = str(numStr).strip().lstrip('-').lstrip('+')    # 去除正数(+)、负数(-)符号
    try:
        reg = re.compile(r'^[-+]?[0-9]+\.[0-9]+$')
        res = reg.match(str(numStr))
        if res:
            flag = True
    except Exception as ex:
        print("is_float() - error: " + str(ex))
    return flag


def is_number(numStr):
    flag = False
    numStr = str(numStr).strip().lstrip('-').lstrip('+')    # 去除正数(+)、负数(-)符号
    if str(numStr).isdigit():
        flag = True
    return flag


def get_opt(opt_path, device, mode, max_motion_length, use_abs3d=False):
    opt = Namespace()
    opt_dict = vars(opt)

    skip = ('-------------- End ----------------',
            '------------ Options -------------',
            '\n')
    print('Reading', opt_path)
    with open(opt_path) as f:
        for line in f:
            if line.strip() not in skip:
                # print(line.strip())
                key, value = line.strip().split(': ')
                if value in ('True', 'False'):
                    opt_dict[key] = bool(value)
                elif is_float(value):
                    opt_dict[key] = float(value)
                elif is_number(value):
                    opt_dict[key] = int(value)
                else:
                    opt_dict[key] = str(value)

    opt_dict['which_epoch'] = 'latest'
    opt.save_root = pjoin(opt.checkpoints_dir, opt.dataset_name, opt.name)
    opt.model_dir = pjoin(opt.save_root, 'model')
    opt.meta_dir = pjoin(opt.save_root, 'meta')

    if opt.dataset_name == 't2m':
        opt.data_root = './dataset/HumanML3D'

        if use_abs3d and mode not in ['eval', 'gt']:
            # Will load the original dataset (relative) if in 'eval' or 'gt' mode
            opt.motion_dir = pjoin(opt.data_root, 'new_joint_vecs_abs_3d')
            print('WARNING: Using absolute 3D coordinates')
        else:
            opt.motion_dir = pjoin(opt.data_root, 'new_joint_vecs') 
            print('WARNING: Using relative 3D coordinates')
        
        opt.text_dir = pjoin(opt.data_root, 'texts')
        opt.joints_num = 22
        opt.dim_pose = 263
        # NOTE: UNET needs to uses multiples of 16
        opt.max_motion_length = max_motion_length
        print(f'WARNING: max_motion_length is set to {max_motion_length}')
    elif opt.dataset_name == 'kit':
        raise NotImplementedError()
        opt.data_root = './dataset/KIT-ML'
        opt.motion_dir = pjoin(opt.data_root, 'new_joint_vecs')
        opt.text_dir = pjoin(opt.data_root, 'texts')
        opt.joints_num = 21
        opt.dim_pose = 251
        opt.max_motion_length = 196
    else:
        raise KeyError('Dataset not recognized')

    opt.dim_word = 300
    opt.num_classes = 200 // opt.unit_length
    opt.dim_pos_ohot = len(POS_enumerator)
    opt.is_train = False
    opt.is_continue = False
    opt.device = device

    pprint(opt)
    
    return opt