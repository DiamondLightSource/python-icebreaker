import collections
import sys
import os
import csv
import pandas as pd
import mrcfile
#from pandas.compat import StringIO
import numpy as np
from itertools import groupby

pd.set_option("display.max_colwidth", 10000)

path_to_star = sys.argv[1]
path_to_micrographs = sys.argv[2]

file = path_to_star

full_path = path_to_micrographs 

last=99999999
header = ''
rC = 0
with open(file, 'r') as f:
	for num,line in enumerate(f,1):
		if '_rln' in line:
			last=num
		
		elif(num>last):
			break
		header += line
		if 'MicrographName' in line:
			micro_name = [int(''.join(s)) for is_digit, s in groupby(line, str.isdigit) if is_digit]

		if 'CoordinateX' in line:
			coord_X = [int(''.join(s)) for is_digit, s in groupby(line, str.isdigit) if is_digit]


		if 'CoordinateY' in line:
			coord_Y = [int(''.join(s)) for is_digit, s in groupby(line, str.isdigit) if is_digit]
		if '_rln' in line:
			rC+=1 


d1 = pd.read_csv(file,sep='\s+',skiprows=last,header=None)

micrographs_used = (d1[:][micro_name[0]-1].unique())

mic_coord = collections.OrderedDict()
for i in range(len(micrographs_used)):
    mic_coord[str(micrographs_used[i])] = (d1.loc[d1[micro_name[0]-1]==str(micrographs_used[i])].index[:]).tolist()

ice_groups =[]
for k in range(len(micrographs_used)):
    print(f'{k} / {len(micrographs_used)}')
    im_path = full_path + os.path.split(str(micrographs_used[k])[:-4])[-1] +'_40x40x16_original_mean.mrc'
    #print((im_path))
    with mrcfile.open(im_path,'r+',permissive=True) as mrc: #! change to right path and patch size
        micro_now = mrc.data
        for i in range(len(mic_coord[micrographs_used[k]])):
            row = (mic_coord[micrographs_used[k]][i])
            x1 = int(np.floor(d1.iloc[row][coord_X[0]-1]))
            y1 = int(np.floor(d1.iloc[row][coord_Y[0]-1]))
            if micro_now is not None:
                ice_groups.append(int(micro_now[y1][x1]*10000))
            else:
                ice_groups.append(-1)

header +=  '_rlnHelicalTubeID #'+str(rC+1)+'\n' # change number 
d2 = pd.DataFrame({'_rlnHelicalTubeID':ice_groups})

result = pd.concat([d1,d2],axis=1,sort=False)
result = result.to_string(header=None,index=None)
with open(file[:-5] + '_icegroups_from_original_mean_scaled.star','w') as fd:
    fd.write(header)
    fd.write(result)

