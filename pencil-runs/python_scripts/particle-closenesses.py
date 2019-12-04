import pencil
import numpy
from matplotlib import pyplot
from matplotlib import cm
import sys
import os

base_path,script_name   = os.path.split(sys.argv[0])
scratch,simulation_name = os.path.split(base_path)
script_name             = script_name[:-3]

data        = pencil.read_var(trimall=True)
pdata       = pencil.read_pvar()
time_series = pencil.read_ts()
parameters  = pencil.read_param()

npar   = len(pdata.ipars)
xgrid  = data.x
ygrid  = data.y
zgrid  = data.z
dxgrid = data.dx
dygrid = data.dy
dzgrid = data.dz
x0 = xgrid[0]
y0 = ygrid[0]
z0 = zgrid[0]
x1 = xgrid[-1]
y1 = ygrid[-1]
z1 = zgrid[-1]
last_snap = numpy.floor(time_series.t[-1]/parameters.tausp) + 1

ivar_lower = 0
ivar_upper = last_snap
if(len(sys.argv) == 3):
    ivar_lower = int(sys.argv[1])
    ivar_upper = int(sys.argv[2])
    nvar       = ivar_upper - ivar_lower + 1
if(ivar_lower < 0 or ivar_upper > last_snap or nvar < 1):
    print("ivar range is not valid. Exiting...")
    sys.exit()
else:
    print("Tracking particle velocities from ivar = " + str(ivar_lower) + " to " + str(ivar_upper))

particle_velocities  = numpy.zeros((npar,nvar))
particle_closenesses = numpy.zeros((npar,nvar))
for ivar in range(ivar_lower,ivar_upper+1):
    var     = "PVAR" + str(ivar)
    pdata = pencil.read_pvar(varfile=var)
    data  = pencil.read_var(ivar=ivar,trimall=True)
    for index in range(npar):
        ipar  = pdata.ipars[index] - 1
        vpz   = pdata.vpz[index]
        particle_velocities[ipar,ivar-ivar_lower] = vpz
        xpar  = pdata.xp[index]
        ypar  = pdata.yp[index]
        zpar  = pdata.zp[index]
        for index2 in range(npar):
            ipar2 = pdata.ipars[index2] - 1
            if(ipar2 == ipar):
                continue
            else:
                x_it = pdata.xp[index2]
                y_it = pdata.yp[index2]
                z_it = pdata.zp[index2]
                particle_closenesses[ipar,ivar-ivar_lower] += ((x_it - xpar)**2 + (y_it - ypar)**2 + (z_it - zpar)**2)**(-0.5)

#
# closeness vs time
#

cvt_fig, ((ax1)) = pyplot.subplots(1,1)
cvt_fig.set_size_inches(19.2,10.8)
cvt_fig.set_dpi(100)

if(nvar == 1):
    ax1.set_xlim(ivar_lower-0.5,ivar_lower+0.5)
    pmarker="o"
else:
    ax1.set_xlim(ivar_lower,ivar_upper)
    pmarker=None
markersize = 10.0

ymin = 1.0e10
ymax = 0
time       = numpy.array(range(ivar_lower,ivar_upper+1))
colors     = cm.get_cmap('viridis')(numpy.linspace(0.0,1.0,npar))
for ipar in range(npar):
    closeness_array = particle_closenesses[ipar]*0.001
    pcolor         = colors[ipar]
    if(closeness_array.min() < ymin):
        ymin = closeness_array.min()
    if(closeness_array.max() > ymax):
        ymax = closeness_array.max()
    ax1.plot(time,closeness_array,linewidth=2.0,marker=pmarker,color=pcolor)

if(ymax < 0.0):
    ymax = ymax + 0.1*(ymax-ymin)
ymin = ymin - 0.1*(ymax-ymin)
ax1.set_ylim(ymin,ymax)
#ax1.set_ylim([-600.0,0.0])

ax1.set_xlabel(r"t ($\tau_{f}$)",fontsize=24)
ax1.set_ylabel(r"closeness (mm$^{-1}$)",fontsize=24)

for tick in ax1.xaxis.get_major_ticks():
    tick.label.set_fontsize(19)
for tick in ax1.yaxis.get_major_ticks():
    tick.label.set_fontsize(19)

cvt_file_title = simulation_name + "_" + script_name + "_" + str(ivar_lower) + "-" + str(ivar_upper) + "_closeness-vs-time.png"
cvt_fig.savefig(cvt_file_title,bbox_inches="tight")

#
# Velocity vs closeness
#

vvc_fig, ((ax2)) = pyplot.subplots(1,1)
vvc_fig.set_size_inches(19.2,10.8)
vvc_fig.set_dpi(100)

for ipar in range(npar):
    closeness_array = particle_closenesses[ipar,4:nvar]*165e-6
    velocity_array = particle_velocities[ipar,4:nvar]*1000.*2.*(-1.0)/37.0
    ax2.scatter(closeness_array,velocity_array,color="black")
#ax2.scatter(particle_closenesses.flatten(),particle_velocities.flatten(),linewidth=2.0,marker=pmarker,color=pcolor)

#if(ymax < 0.0):
#    ymax = ymax + 0.1*(ymax-ymin)
#ymin = ymin - 0.1*(ymax-ymin)
#ax2.set_ylim(ymin,ymax)
#ax2.set_ylim([-600.0,0.0])

ax2.set_xlim([0.0,10.0])

ax2.set_xlabel(r"closeness$\cdot r_{p}$",fontsize=24)
ax2.set_ylabel(r"$v_{rel}$ (mm $s^{-1}$)",fontsize=24)

for tick in ax2.xaxis.get_major_ticks():
    tick.label.set_fontsize(19)
for tick in ax2.yaxis.get_major_ticks():
    tick.label.set_fontsize(19)

vvc_file_title = simulation_name + "_" + script_name + "_" + str(ivar_lower) + "-" + str(ivar_upper) + "_velocity-vs-closeness.png"
vvc_fig.savefig(vvc_file_title,bbox_inches="tight")

#
# mean velocity vs mean closeness
#

mvvmc_fig, ((ax3)) = pyplot.subplots(1,1)
mvvmc_fig.set_size_inches(19.2,10.8)
mvvmc_fig.set_dpi(100)

marker_size  = 15.0
marker_color = "black"
marker_style = "^"

ymin = 1.0e10
ymax = 0
closeness_mean = numpy.zeros(nvar-4)
velocity_mean  = numpy.zeros(nvar-4)
for ivar in range(4,nvar):
    imean = ivar - 4
    closeness_array = particle_closenesses[:,ivar]*165e-6
    velocity_array = particle_velocities[:,ivar]*1000.*2.*(-1.0)/37.0
    closeness_mean[imean] = closeness_array.mean()
    velocity_mean[imean]  = velocity_array.mean()
    if(velocity_mean.min() < ymin):
        ymin = velocity_mean.min()
    if(velocity_mean.max() > ymax):
        ymax = velocity_mean.max()
ax3.plot(closeness_mean,velocity_mean,linestyle=None,marker=marker_style,markerfacecolor=marker_color,markeredgecolor=marker_color,markersize=marker_size)

if(ymax < 0.0):
    ymax = ymax + 0.1*(ymax-ymin)
ymin = ymin - 0.1*(ymax-ymin)
ax3.set_ylim(ymin,ymax)
#ax3.set_ylim([-600.0,0.0])

ax3.set_xlim([0.0,10.0])

ax3.set_xlabel(r"closeness$\cdot r_{p}$",fontsize=24)
ax3.set_ylabel(r"$\bar{v}_{rel}$ (mm $s^{-1}$)",fontsize=24)

for tick in ax3.xaxis.get_major_ticks():
    tick.label.set_fontsize(19)
for tick in ax3.yaxis.get_major_ticks():
    tick.label.set_fontsize(19)

mvvmc_file_title = simulation_name + "_" + script_name + "_" + str(ivar_lower) + "-" + str(ivar_upper) + "_mean-velocity-vs-mean-closeness.png"
mvvmc_fig.savefig(mvvmc_file_title,bbox_inches="tight")

pyplot.show()