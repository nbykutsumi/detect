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


iYear  = 2006
eYear  = 2015

#-- argv ----------------
largv = sys.argv
if len(largv)>1:
  prj, model, run, res, noleap = largv[1:1+5]
  noleap     = bool(noleap)
  iYear, eYear = map(int,largv[6:6+2])
#-------------------------

lYear = range(iYear,eYear+1)

#var   = "pwat"
#var   = "spfh_2lev"
var   = "spfh_3lev"

lev   = False  # For 850_500, 850_500_250

ret_lDTime = {False: util.ret_lDTime
             ,True : util.ret_lDTime_noleap
             }[noleap]

cfg    = config_func.config_func(prj, model, run)
iom    = IO_Master.IO_Master(prj, model, run, res)
cfg["res"] = res

miss  = -9999.
ny    = iom.ny
nx    = iom.nx
a1lat = iom.Lat
a1lon = iom.Lon
ms    = Monsoon.MonsoonMoist(cfg)
#-----------------------------------
def ret_a2var(var, lev=False):
  if var in ["spfh"]:
    return iom.Load_day_spfh(DTime,lev=lev)

  elif var == "spfh_2lev":
    a2var1 = iom.Load_day_spfh(DTime, plev=850)
    a2var2 = iom.Load_day_spfh(DTime, plev=500)
    return (a2var1 + a2var2)/2.0

  elif var == "spfh_3lev":
    a2var1 = iom.Load_day_spfh(DTime, plev=850)
    a2var2 = iom.Load_day_spfh(DTime, plev=500)
    a2var3 = iom.Load_day_spfh(DTime, plev=250)
    return (a2var1 + a2var2 + a2var3)/3.0
  else:
    print "Check var:",var
    sys.exit()
#-----------------------------------

for Year in lYear:
  iDTime = datetime(Year,1,1,0)
  #eDTime = datetime(2014,1,5,0)
  eDTime = datetime(Year,12,31,0)
  dDTime = timedelta(hours=24)
  lDTime = ret_lDTime(iDTime, eDTime, dDTime)
  nDay   = len(lDTime)
  a3dat  = zeros([nDay, ny, nx], float32)
  
  for i,DTime in enumerate(lDTime):
    print DTime
    #a2in  = ra.time_ave(var, DTime, DTime+timedelta(hours=23), timedelta(hours=6),lev=lev)
    a2in   = ret_a2var(var, lev=lev)
    a3dat[i] = a2in
  #
  a2max = a3dat.max(axis=0)
  a2min = a3dat.min(axis=0)

  #oDir      = ms.baseDir + "/ms_minmax/%s"%(var)
  #MaxPath   = oDir + "/max.%04d.bn"%(Year)
  #MinPath   = oDir + "/min.%04d.bn"%(Year)

  oDir      = ms.pathMinMax(var, Year, "max")[0]
  MaxPath   = ms.pathMinMax(var, Year, "max")[-1]
  MinPath   = ms.pathMinMax(var, Year, "min")[-1]

  util.mk_dir(oDir)
  a2max.astype(float32).tofile(MaxPath)
  a2min.astype(float32).tofile(MinPath)
  print MaxPath
  
  
    
