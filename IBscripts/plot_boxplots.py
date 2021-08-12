import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mrcfile
import cv2
import os
import seaborn as sns
import argparse

def plot_boxes(indir):
	files = []

	for filename in os.listdir(indir):
		if (filename.endswith(".mrc")):
			finalpath = os.path.join(indir,filename)
			files.append(finalpath)
		else:
			continue
	files = sorted(files)
	vector_data = []
	for img_path in files:
		with mrcfile.open(img_path, 'r', permissive=True) as mrc:
			img = mrc.data
			a_vector = np.reshape(img,-1)
			vector_data.append(a_vector)
	labels = []
	for label in files:
		splitpath = os.path.split(label)
		labels.append(splitpath[-1][:-4])
	fig = plt.figure()
	ax = fig.add_subplot(111)
	ax.boxplot(vector_data,0,'x')
	ax.set_xticklabels(labels,rotation=90,fontsize=8)

	plt.yticks(fontsize=10)
	plt.ylabel('Pixel intensity',fontsize =12)
	plt.xlabel('Micrographs', fontsize=12)
	plt.grid(axis='y')
	plt.tight_layout()
	plt.show()

def main():
	parser=argparse.ArgumentParser()
	parser.add_argument("in_dir",help="Path to directory with micrographs_grouped",type=str)
	args = parser.parse_args()
	indir = args.in_dir
	plot_boxes(indir)
if __name__ == '__main__':
	sys.exit(main())
