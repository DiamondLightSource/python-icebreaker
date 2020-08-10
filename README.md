# ICEBREAKER

The Icebreaker software for ice gradient estimation and removal on cryoEM micrographs.

External job for calling IceBreaker grouping within Relion 3.1
in_parts is input star file from relion picking job 
in_mics is previous grouping job directory
 
Run in main Relion project directory

## Processing the micrographs

To process the micrographs use the ib_job.py script 

As an input, it takes a .star file with a list of micrographs to process, e.g. micrographs_ctf.star

In the 'Params' tab, you have to add a label **mode** which can take values **group** (it will group areas with similar ice thickness) or **flatten** (it will improve contrasts locally trying to remove the ice gradient). 

In the Running tab use the slider to select the number of threads. 

The output from this job is a new set of micrographs.


## Processing the particles

As 'Input micrographs' it takes micrographs 'grouped' with the previous script. As 'Input particles' any star file with particles from jobs like Extract particles, 2D classes, etc. It takes no additional parameters and this is single-threaded. As a result, additional parameter column (\_ibIceGroup) with estimated ice thickness value for each particle will be added.


## Using the job templates

To make it easier to get started running Icebreaker from Relion, you can use one of the template star files *ib\_job\_template\_GROUP\_MODE.star*, *ib\_job\_template\_FLATTEN\_MODE.star* or *ib\_group\_template.star*. To use a template:

1. Copy one of the templates to your Relion project directory as *.gui\_externaljob.py*
2. Select the External job type
3. Click Jobs -> Load job settings
4. Change the placeholder input names to select your input files
5. Choose your running options and run the job as normal

