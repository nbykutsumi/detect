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
prj     = "JRA55"
model   = "__"
run     = "__"
res     = "145x288"
noleap  = False

#prj     = "HAPPI"
#model   = "MIROC5"
#run     = "C20-ALL-001"
#res     = "128x256"
#noleap  = True

iDTime = datetime(2006,1,1,0)    # HAPPI
eDTime = datetime(2015,12,31,0)  # HAPPI

iYearMinMax = 2006
eYearMinMax = 2014

#iDTimeData = datetime(2006,1,1,0)   # JRA55
#eDTimeData = datetime(2015,8,31,0)  # JRA55
iDTimeData = datetime(2006,1,1,6)    # HAPPI
eDTimeData = datetime(2016,12,31,18) # HAPPI

#-- argv ----------------
largv = sys.argv
if len(largv)>1:
  prj, model, run, res, noleap = largv[1:1+5]
  noleap     = bool(noleap)
  iYear,iMon, eYear, eMon  = map(int,largv[6:6+4])
  iYearMinMax, eYearMinMax = map(int,largv[10:10+2])
  iYearData,   eYearData   = map(int,largv[12:12+2])

  iDTime = datetime(iYear,iMon,1,6)
  eDTime = datetime(eYear,eMon,31,18)

  iDTimeData = datetime(iYearData,1,1,6)    
  eDTimeData = datetime(eYearData,12,31,18)

#-------------------------



dDTime = timedelta(days=1)

ret_lDTime = {False: util.ret_lDTime
             ,True : util.ret_lDTime_noleap
             }[noleap]

lDTime   = ret_lDTime(iDTime, eDTime, dDTime)

#--------------------------------
# Set lDTime_extend : +-2days extension
if noleap == True:
  if ((iDTime==datetime(iDTime.year,3,1))or(iDTime==datetime(iDTime.year,3,2))):
    iDTime_extend = iDTime - timedelta(days=3)
  else:
    iDTime_extend = iDTime - timedelta(days=2)

  if ((eDTime==datetime(eDTime.year,2,27))or(eDTime==datetime(eDTime.year,2,28))):
    eDTime_extend = eDTime + timedelta(days=3)
  else:
    eDTime_extend = eDTime + timedelta(days=2)

else:
  iDTime_extend = iDTime - timedelta(days=2)
  eDTime_extend = eDTime + timedelta(days=2)

lDTime_extend = ret_lDTime(iDTime_extend, eDTime_extend, dDTime)
#--------------------------------


cfg    = config_func.config_func(prj, model, run)
cfg["res"] = res

iom    = IO_Master.IO_Master(prj, model, run, res)
ny     = iom.ny
nx     = iom.nx
miss   = -9999.

#var   = "pwat"
#var   = "spfh_2lev"
var   = "spfh_3lev"

ms  = Monsoon.MonsoonMoist(cfg)
ms.prepMonsoonMoist(var, iYearMinMax, eYearMinMax)
for i,DTime in enumerate(lDTime):
  lDTime_mean = lDTime_extend[i+2-2:i+2-2+5] 

  try:
    a2ms  = ms.mkMonsoonMoist(var, lDTime_mean, miss_out=miss)
  except IOError:
    if (DTime < iDTimeData + timedelta(days=2)):
      a2ms  = ones([ny,nx], float32)*miss
    elif (DTime > eDTimeData - timedelta(days=2)):
      a2ms  = ones([ny,nx], float32)*miss

  sDir, sPath = ms.pathMonsoonMoist(var, DTime)
  util.mk_dir(sDir)
  a2ms.astype(float32).tofile(sPath)
  print sPath

