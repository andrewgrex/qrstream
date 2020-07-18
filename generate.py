import sys
import segno
import os
import pathlib
import argparse
import base64

parser = argparse.ArgumentParser(description='Create QR codes for chunks of a file')
parser.add_argument('-f', '--filepath', type=str, help='path to file to chunk')
parser.add_argument('-qf', '--qrdirectory', type=str, help='directory for qr code outputs')
parser.add_argument('-b', '--blocksize', type=int, default=1024, help='size of each chunk (default=1024)')
args = parser.parse_args()

def filesystem_setup(qr_folder, filepath):
	if not os.path.isdir(qr_folder):
	    os.mkdir(qr_folder)

	fn = filepath.split('/')[-1].split('.')[0]
	imgs_dir = pathlib.Path(qr_folder) / fn
	if not os.path.isdir(imgs_dir):
	    os.mkdir(imgs_dir)
	return imgs_dir


def chunked(filepath, imgs_dir, blocksize=1024):

	BUF  = 50*1024*1024*1024  # 50GB   - memory buffer size

	idx = 0
	with open(filepath, 'rb') as src:
	    while True:
	        written = 0
	        while written < blocksize:
	            data = src.read(min(BUF, blocksize - written))
	            if not data:
	                break

	            # merge qr code index to data 
	            combined_bytes = (idx).to_bytes(8, byteorder='big') + data

	            # encode to base64 (this way we can send as alphanumeric)
	            combined_bytes = base64.b64encode(combined_bytes)

	            print(f"[INFO] iteration: {idx}; len: {len(combined_bytes)}")
	            
	            qr = segno.make(combined_bytes)
	            qr.save(pathlib.Path(imgs_dir / f'{idx}.png')) 
	            idx += 1
	        
	            written += min(BUF, blocksize - written)
	            if written == 0:
	                break

	        if not written:
	                break


if __name__ == '__main__':

	# setup file system 
	imgs_dir = filesystem_setup(args.qrdirectory, args.filepath)

	# chunk the file and create qr codes
	chunked(args.filepath, imgs_dir, args.blocksize)
