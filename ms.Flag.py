from numpy import *
from detect_fsub import *
from datetime import datetime, timedelta
import myfunc.util as util
import config_func
import IO_Master
import Cyclone
import calendar
import os, sys
import Monsoon
import myfunc.fig.Fig as Fig
##***************************
#prj     = "JRA55"
#model   = "__"
#run     = "__"
#res     = "145x288"
#noleap  = False

prj     = "HAPPI"
model   = "MIROC5"
run     = "C20-ALL-001"
res     = "128x256"
noleap  = True

var   = "spfh_3lev"
iYear = 2006
eYear = 2014
lYear = range(iYear,eYear+1)

cfg  = config_func.config_func(prj=prj, model=model, run=run)
cfg["res"] = res
ms   = Monsoon.MonsoonMoist(cfg)

iom  = IO_Master.IO_Master(prj, model, run, res)
ny   = iom.ny
nx   = iom.nx
Lat  = iom.Lat
Lon  = iom.Lon
miss = -9999.
for Mon in range(1,12+1):
  a2count = zeros([ny,nx],float32)
  for Year in lYear:
    print Mon, Year
    iDay = 1

    eDay = calendar.monthrange(Year,Mon)[1]
    if ((noleap==True)&(Mon==2)):
      eDay = 28

    lDay = range(iDay, eDay+1)
  
    for Day in lDay:
      DTime = datetime(Year, Mon, Day, 0)
      a2ms  = ms.loadMonsoonMoist(var, DTime, maskflag=True).filled(0.0)
      a2count = a2count + a2ms
  
  a2region= ms.loadRegionW14(iYear,eYear)
  a2count = a2count / float(len(lYear))
  a2count = ma.masked_less_equal(a2count, 0.0)
  a2count = ma.masked_where(a2region==miss, a2count)
  #-- Figure --------
  sDir  = "/home/utsumi/mnt/wellshare/HAPPI/anlWS/ms.count"
  figPath = sDir + "/count.%s.%s.%s.%02d.png"%(prj,model,run,Mon)
  util.mk_dir(sDir)
  stitle = "%s %s %s"%(prj,model,run) + "\n"
  stitle = stitle + "%04d-%04d Mon=%02d"%(iYear,eYear,Mon)
  Fig.DrawMapSimple(a2count, a1lat=Lat, a1lon=Lon, BBox = [[-80, 0], [80,360]], figname=figPath, vmax=31, vmin=0.0, stitle=stitle, cmap="jet")
