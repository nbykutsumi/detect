from numpy import *
from detect_fsub import *
from datetime import datetime, timedelta
import util
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
eYear  = 2014

#-- argv ----------------
largv = sys.argv
if len(largv)>1:
  prj, model, run, res, noleap = largv[1:1+5]
  noleap     = bool(noleap)
  iYear, eYear = map(int,largv[6:8])
#-------------------------

lYear  = range(iYear,eYear+1)

cfg    = config_func.config_func(prj, model, run)
iom    = IO_Master.IO_Master(prj, model, run, res)

cfg["res"] = res

miss  = -9999.
ny    = iom.ny
nx    = iom.nx
a1lat = iom.Lat
a1lon = iom.Lon
ms    = Monsoon.MonsoonMoist(cfg)

def Region5Mon(iYear,eYear):
  lYear  = range(iYear,eYear+1)
  a2var0 = zeros([ny,nx],float32)
  a2var1 = zeros([ny,nx],float32)
  a2var2 = zeros([ny,nx],float32)

  for Year in lYear:
    for Mon in range(1,12+1):
      a2var0 = a2var0 + iom.Load_monPrcp_mmd(Year,Mon)
      if Mon in [5,6,7,8,9]:
        a2var1 = a2var1 + iom.Load_monPrcp_mmd(Year,Mon)
      if Mon in [11,12,1,2,3]:
        a2var2 = a2var2 + iom.Load_monPrcp_mmd(Year,Mon)

  a2var0 = a2var0/ len(lYear) /12 
  a2var1 = a2var1/ len(lYear) /5
  a2var2 = a2var2/ len(lYear) /5
  a2summer = r_[ a2var2[:ny/2,:], a2var1[ny/2:,:]]
  a2winter = r_[ a2var1[:ny/2,:], a2var2[ny/2:,:]]

  a2dif  = (a2summer - a2winter)
  return ma.masked_where(a2summer<= a2var0*0.55, a2dif)

def RegionZL04(iYear,eYear):
  var    = "pwat"
  lYear  = range(iYear,eYear+1)

  a3var1 = zeros([3,ny,nx],float32)
  for i,Mon in enumerate([6,7,8]):
    for Year in lYear:
      a3var1[i] = a3var1[i] + iom.Load_monSfc(var, Year,Mon)
    a3var1[i] = a3var1[i]/len(lYear)

  a3var2 = zeros([3,ny,nx],float32)
  for i,Mon in enumerate([12,1,2]):
    for Year in lYear:
      a3var2[i] = a3var2[i] + iom.Load_monSfc(var, Year,Mon)
    a3var2[i] = a3var2[i]/len(lYear)

  a2max = r_[ a3var2[:,:ny/2,:].max(axis=0), a3var1[:,ny/2:,:].max(axis=0)]
  a2min = r_[ a3var1[:,:ny/2,:].min(axis=0), a3var2[:,ny/2:,:].min(axis=0)]

  return a2max - a2min

#------------------------------------------------

a2rg  = Region5Mon(iYear,eYear)
#a2rg2 = RegionZL04(iYear,eYear)
#a2rg  = ma.masked_where(a2rg2<=12, a2rg)
#a2out = ma.masked_where(a2rg<2.0, ones([ny,nx],float32))
a2out = ma.masked_where(a2rg<3.0, ones([ny,nx],float32))
a2out = a2out.filled(miss)

rootDir, srcDir, srcPath = ms.pathRegionW14(iYear,eYear)
util.mk_dir(srcDir)
a2out.tofile(srcPath)
print srcPath

#----- Figure ----------------
#a2fig   = r_[a2out[:,nx/2:], a2out[:,:nx/2]]
a2fig   = a2out
a2fig   = ma.masked_equal(a2fig, miss)
figname = srcPath + ".png"
BBox    = [[-90,0],[90,360]]
stitle  = "%s %s %s"%(prj,model,run)
Fig.DrawMapSimple(a2in=a2fig, a1lat=a1lat, a1lon=a1lon, figname=figname, BBox=BBox, vmax=3., stitle=stitle)



