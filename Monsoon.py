from numpy import *
from datetime import datetime, timedelta
import os, sys
import socket
import IO_Master
import myfunc.util as util
import calendar

def read_txtlist(iname):
  f = open(iname, "r")
  lines = f.readlines()
  f.close()
  lines = map(float, lines)
  aout  = array(lines, float32)
  return aout

def Check9grids(a2flag,miss_out=-9999.):
  ny,nx    = shape(a2flag)
  a2countN = r_[a2flag[0,:].reshape(1,nx),  a2flag[:-1,:]]
  a2countS = r_[a2flag[1:,:], a2flag[-1, :].reshape(1,nx)]

  a2count  = a2flag
  a2count  = a2count + c_[a2flag[:,1:], a2flag[:,0]]
  a2count  = a2count + c_[a2flag[:,-1], a2flag[:,:-1]]
  a2count  = a2count + a2countN
  a2count  = a2count + a2countS
  a2count  = a2count + c_[a2countN[:,1:], a2countN[:,0]]
  a2count  = a2count + c_[a2countN[:,-1], a2countN[:,:-1]]
  a2count  = a2count + c_[a2countS[:,1:], a2countS[:,0]]
  a2count  = a2count + c_[a2countS[:,-1], a2countS[:,:-1]]
  return ma.masked_where(a2count <7, ones([ny,nx], float32)).filled(miss_out)


class MonsoonMoist(object):
  #def __init__(self, model="JRA55", res="bn", var="pwat",miss=-9999.):
  def __init__(self, cfg, miss=-9999.):
    #----------------
    self.cfg   = cfg
    self.prj   = cfg["prj"  ]
    self.model = cfg["model"]
    self.run   = cfg["run"  ]
    self.res   = cfg["res"  ]

    self.rootDir = cfg["rootDir"]
    self.baseDir = cfg["baseDir"]

    self.Lat     = read_txtlist( os.path.join(self.baseDir, "lat.txt"))
    self.Lon     = read_txtlist( os.path.join(self.baseDir, "lon.txt"))
    self.ny      = len(self.Lat)
    self.nx      = len(self.Lon)
    self.miss    = miss

    self.thrat  = 0.618
    #self.dPWAT  = {"JRA55":"PWAT"}
    #self.dSPFH  = {"JRA55":"spfh"}
    #self.dstypePWAT = {"JRA55":"anl_column125"}
    #self.dstypeSPFH = {"JRA55":"anl_p125"}

    self.iom    = IO_Master.IO_Master(
                    self.prj, self.model, self.run, self.res
                                    )

  def prepMonsoonMoist(self, var, iYearMinMax, eYearMinMax):
    iY = iYearMinMax
    eY = eYearMinMax 
    self.a2min    = self.mkAveMinMax(var, iY, eY, maxmin="min")
    self.a2max    = self.mkAveMinMax(var, iY, eY, maxmin="max")
    self.a2region = self.loadRegionW14(iY, eY)

  def pathRegionW14(self, iYear, eYear):
    srcDir  = self.baseDir + "/msregion/W14"
    srcPath = srcDir  + "/region.%04d-%04d.%s"%(iYear,eYear,self.res)
    return self.baseDir, srcDir, srcPath

  def loadRegionW14(self, iYear, eYear):
    srcPath = self.pathRegionW14(iYear, eYear)[-1]
    return fromfile(srcPath, float32).reshape(self.ny, self.nx)

  def pathMinMax(self, var, Year, maxmin="max"):
    srcDir   = self.baseDir + "/ms_minmax/%s"%(var)
    srcPath  = srcDir + "/%s.%04d.%s"%(maxmin, Year, self.res)
    return srcDir, srcPath

  def mkAveMinMax(self, var, iYear,eYear,maxmin="max"):
    ny,nx  = self.ny, self. nx
    miss   = self.miss
    lYear  = range(iYear,eYear+1)
    a3dat  = zeros([len(lYear), self.ny, self.nx])
    for i,Year in enumerate(lYear):
      sPath     = self.pathMinMax(var, Year, maxmin)[-1]
      a2in      = ma.masked_equal(fromfile(sPath, float32).reshape(ny,nx), miss)
      a3dat[i]  = a2in
    return a3dat.mean(axis=0)

  def mkDailyVar(self, var, DTime):
    if var in ["spfh"]:
      return self.iom.Load_day_spfh(DTime,lev=lev)
  
    elif var == "spfh_2lev":
      a2var1 = self.iom.Load_day_spfh(DTime, plev=850)
      a2var2 = iom.Load_day_spfh(DTime, plev=500)
      return (a2var1 + a2var2)/2.0
  
    elif var == "spfh_3lev":
      a2var1 = self.iom.Load_day_spfh(DTime, plev=850)
      a2var2 = self.iom.Load_day_spfh(DTime, plev=500)
      a2var3 = self.iom.Load_day_spfh(DTime, plev=250)
      return (a2var1 + a2var2 + a2var3)/3.0
    else:
      print "Check var:",var
      sys.exit()

  def pathMonsoonMoist(self, var, DTime):
    model   = self.model
    res     = self.res
    rootDir = self.rootDir
    Year    = DTime.year
    Mon     = DTime.month
    Day     = DTime.day 
 
    srcDir  = self.baseDir + "/6hr/ms"
    srcPath = srcDir  + "/ms.%04d.%02d.%02d.%s"%(Year,Mon,Day,res)
    return srcDir, srcPath


  def mkMonsoonMoist(self, var, lDTime, miss_out=-9999.):
    model   = self.model
    ny, nx  = self.ny, self.nx
    a2var   = zeros([ny,nx],float32)
    for DTime in lDTime:
      a2var = a2var + self.mkDailyVar(var, DTime)

    a2var   = a2var / len(lDTime)
       
    a2npwi = (a2var - self.a2min)/(self.a2max-self.a2min)
    #a2out  = ma.masked_where(a2npwi<self.thrat, ones([ny,nx],float32)).filled(miss_out)
    a2out  = ma.masked_where(a2npwi<self.thrat, ones([ny,nx],float32)).filled(0.0)
    a2out  = Check9grids(a2out,miss_out=miss_out)
    return ma.masked_where(self.a2region==self.miss, a2out).filled(miss_out)

  def loadMonsoonMoist(self, var, DTime, maskflag=False):
    sPath  = self.pathMonsoonMoist(var, DTime)[-1]
    if maskflag == False:
      return fromfile(sPath, float32).reshape(self.ny, self.nx)
    elif maskflag == True:
      return ma.masked_equal(fromfile(sPath, float32).reshape(self.ny, self.nx), self.miss)
