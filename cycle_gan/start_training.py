import subprocess
import itertools
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--experiment", type=str, required=True)
parser.add_argument("--data_root", type=str, required=True)
parser.add_argument("--setup", type=int, required=False, default=0)
parser.add_argument("--submit_cmd", type=str, required=False, default="python")


def start_training(train_setup,
                   data_roots,
                   netG="resnet_9blocks",
                   in_size=128,
                   continue_train=False,
                   submit_cmd="python",
                   input_nc=1,
                   output_nc=1,
                   crop_size=None,
                   preprocess="none"):

    if crop_size is None:
        crop_size = in_size

    for data_root in data_roots:
        base_cmd = f"{submit_cmd} -u cycle_gan/train.py" +\
                   " --dataroot {} --name {} --input_nc {} --output_nc {} --netG {} --load_size {}"+\
                   " --crop_size {} --checkpoints_dir {} --display_id 0"+\
                   " --preprocess {}"

        if continue_train:
            base_cmd += " --continue_train"

        train_setup_name = "train_s{}".format(train_setup)
        checkpoint_dir = os.path.join(os.path.join(data_root, "setups"), 
                                      train_setup_name)

        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        cmd = base_cmd.format(data_root,
                              train_setup_name,
                              input_nc,
                              output_nc,
                              netG,
                              in_size,
                              in_size,
                              checkpoint_dir,
                              preprocess)
        subprocess.Popen(cmd, 
                         shell=True) 

def train_cats_dogs(train_setup, data_root, submit_cmd):
    """
    avg width:  404.09904 avg_height:  360.47808 avg_side:  382.288
    use closest divisible by 4 -> 384
    we use this as load size and crop down to 256
    """
    datasets = ["cats_dogs"]

    data_roots = []
    for d in datasets:
        data_roots.append(f"{data_root}/{d}")

    start_training(train_setup=train_setup, 
                   data_roots=data_roots,
                   in_size=384,
                   crop_size=256,
                   submit_cmd=submit_cmd,
                   input_nc=3,
                   output_nc=3,
                   preprocess="resize_and_crop")

def train_mnist(train_setup, data_root, submit_cmd):
    datasets = [f"{i}_{j}" for i,j in list(itertools.combinations([k for k in range(10)], 2))]

    data_roots = []
    for d in datasets:
        data_roots.append(f"{data_root}/{d}")

    start_training(train_setup=train_setup, 
                   data_roots=data_roots,
                   in_size=28, 
                   submit_cmd=submit_cmd)

def train_disc_a(train_setup, data_root, submit_cmd):
    datasets = ["0_1"]

    data_roots = []
    for d in datasets:
        data_roots.append(f"{data_root}/{d}")

    start_training(train_setup=train_setup, 
                   data_roots=data_roots,
                   in_size=128,
                   submit_cmd=submit_cmd)


def train_disc_b(train_setup, data_root, submit_cmd):
    datasets = ["0_1", "0_2", "1_2"] 

    data_roots = []
    for d in datasets:
        data_roots.append(f"{data_root}/{d}")

    start_training(train_setup=train_setup, 
                   data_roots=data_roots,
                   in_size=128,
                   submit_cmd=submit_cmd)

def train_synapses(train_setup, data_root, submit_cmd):
    classes = ["gaba", "acetylcholine", "glutamate","serotonin", "octopamine", "dopamine"]
    datasets = [f"{i}_{j}" for i,j in list(itertools.combinations([k for k in classes], 2))]

    data_roots = []
    for d in datasets:
        data_roots.append(f"{data_root}/{d}")

    start_training(train_setup=train_setup, 
                   data_roots=data_roots,
                   in_size=128,
                   submit_cmd=submit_cmd)

if __name__ == "__main__":
    exp_to_f = {"mnist": train_mnist,
                "synapses": train_synapses,
                "disc_a": train_disc_a,
                "disc_b": train_disc_b,
                "cats_dogs": train_cats_dogs}

    args = parser.parse_args()
    f_train = exp_to_f[args.experiment]
    f_train(args.setup, args.data_root, args.submit_cmd)
