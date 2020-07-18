import glob
import os
import pathlib
import time
import argparse
import matplotlib  
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Play QR codes to screen in a sequence')
parser.add_argument('-fp', '--qrdirectory', type=str, help='directory for qr code outputs')
parser.add_argument('-f', '--freq', type=float, default=1, help='number of frames per second')
args = parser.parse_args()


def animate(freq, imgs_dir):
    max_idx = len(glob.glob(f"{imgs_dir}/*"))

    files = []
    for idx in range(0, max_idx):
        files.append(f'{imgs_dir}/{idx}.png')


    plt.figure(1); plt.clf()
    plt.pause(5)

    img = None
    for idx,f in enumerate(files):

        plt.figure(1); plt.clf()
        plt.axis('off')

        im=plt.imread(f)
        print(f"[INFO] showing image: {idx}/{len(files)}")
        img = plt.imshow(im, cmap="gray")
        
        plt.pause(1 / args.freq)

if __name__ == '__main__':
    
    # animate the qr codes
    animate(args.freq, args.qrdirectory)
