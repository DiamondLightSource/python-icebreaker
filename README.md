# ICEBREAKER

The Icebreaker software for ice gradient estimation and removal on cryoEM micrographs.

External job for calling IceBreaker grouping within Relion 3.1
in _parts is input star file from relion picking job 
in_mics is previous grouping job directory
 
Run in main Relion project directory

## Processing the micrographs
To process the micragraphs use the ib_job.py script 

As an input, it takes a .star file with a list of micrographs to process, e.g. micrographs_ctf.star

In the 'Params' tab, you have to add a label **mode** which can take values **group** (it will group areas with similar ice thickness) or **flatten** (it will improve contrasts locally trying to remove the ice gradient). 

In the Running tab use the slider to select the number of threads. 

The output from this job is a new set of micrographs.


## Processing the particles

As 'Input micrographs' it takes micrographs 'grouped' with the previous script. As 'Input particles' any star file with particles from jobs like Extract particles, 2D classes, etc. It takes no additional parameters and this is single-threaded. As a result, additional parameter column (\_rlnHelicalTubeID) with estimated ice thickness value for each particle will be added.
