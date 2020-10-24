import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scraper import *
import subprocess
import sys
import os
# Dictionary with color/line marker information, to stay consistent
prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']
markers = ['o','x']
lines = ['solid','dashed']
style_map = {}
p = 1
for line, marker in zip(lines,markers):
    for color in colors:
        style_map[p]=(color,line,marker)
        p += 1

def parse_input(input_file):
    regex="MPItasks=(.+?) OMPthreads=(.+?) NRepetitions=(.+?) Ndim=(.+?) N=(.+?) Nelements=(.+?) elapsed time=(.+?) GDOF\/s=(.+?) GB\/s=(.+?) GFLOPS\/s=(.+)"
    data = field_by_regex(regex,input_file)
    table={}
    for entry in data:
      mpi_ranks = int(entry[0])
      nthreads = int(entry[1])
      nreps = int(entry[2])
      ndim = int(entry[3])
      n = int(entry[4])
      nelem = int(entry[5])
      time = float(entry[6])
      dofRate = float(entry[7])
      bw = float(entry[8])
      flopRate = float(entry[9])
      if (n,ndim) not in table.keys():
        table[(n,ndim)] = ([dofRate * time * 1e9],[flopRate],[bw])
      else:
        table[(n,ndim)][0].append(dofRate * time * 1e9)
        table[(n,ndim)][1].append(flopRate)
        table[(n,ndim)][2].append(bw)
    return table

def generate_plot(filename,ndim,xlim,ylim,bkmode, machine="V100", bw=False, style_map = style_map):
    data = parse_input(filename)
    plt.clf()
    for order, dim in data.keys():
        if not dim == ndim:
            continue
        color, line_type, marker_type = style_map[order]
        dofs = data[(order,dim)][0]
        dofs = np.array(dofs)
        idx = np.argsort(dofs)
        dofs = dofs[idx]
        if bw:
            rate = data[(order,dim)][2]
        else:
            rate = data[(order,dim)][1]
        rate = np.array(rate)
        rate = rate[idx]
        plt.semilogx(dofs, rate, color=color, linestyle=line_type, marker=marker_type, label=f"p={order}")
    filestr = ""
    title = ""
    ylabel = ""
    if bw:
        filestr = f"{machine}_bw_bk_{bkmode}_ndim_{ndim}"
        title = f"BK5 Bandwidth Rates, {machine}"
        ylabel = "GB/s"
    else:
        filestr = f"{machine}_flop_rate_bk_{bkmode}_ndim_{ndim}"
        title = f"BK5 Flop Rates Rates, {machine}"
        ylabel = "GFLOPS"
    plt.title(title)
    plt.xlabel("Degrees of Freedom")
    plt.ylabel(ylabel)
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend()
    plt.savefig(filestr,dpi=300)
    plt.clf()

machine_to_gpu = {
  "tulip" : [ "mi60", "mi100", "v100" ],
  "summit" : [ "v100" ],
  "thetagpu" : ["a100"]
}
for machine_name, gpu_types in machine_to_gpu.items():
  for gpu_type in gpu_types:
    os.chdir(f"/home/malachi/work/research/nekbench-results/Figs/{machine_name}/{gpu_type}")
    for bk_mode in [0,5]:
      for ndim in [1,3]:
        filename = f"/home/malachi/work/research/nekbench-results/data/{machine_name}/{gpu_type}/kernel_version_0_bk_mode_{bk_mode}_results"
        generate_plot(filename,ndim,xlim=(1e3,1e8), ylim=(0,3250), bkmode=bk_mode, machine=gpu_type, bw=False)
        generate_plot(filename,ndim,xlim=(1e3,1e8), ylim=(0,1300), bkmode=bk_mode, machine=gpu_type, bw=True)



