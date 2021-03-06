#!/bin/bash
# Standard output and error:
#SBATCH -o ./hb_dtog-1.36e-1_64x64x130.out.%j
#SBATCH -e ./hb_dtog-1.36e-1_64x64x130.err.%j
#SBATCH -D ./
#SBATCH -J hb_dtog-1.36e-1_64x64x130
#SBATCH --nodes=2
#SBATCH --tasks-per-node=40
#SBATCH --cpus-per-task=1
#SBATCH --mail-type=all
#SBATCH --mail-user=carpenter@mpia.de
# Wall clock limit
#SBATCH --time=12:05:00

pc_run -f $PENCIL_HOME/config/hosts/isaac/isaac1.bc.rzg.mpg.de.conf
