from numpy import *
from collections import deque
from   datetime import datetime, timedelta
import sys
import util
import config_func
import Cyclone

#prj   = "JRA55"
#model = "__"
#run   = "__"
#res   = "125x288"
#noleap= False
##iYear_data = 1958
##iMon_data  = 1
#iYear_data = 2004
#iMon_data  = 1

prj     = "HAPPI"
model   = "MIROC5"
run     = "C20-ALL-001"
res     = "128x256"
noleap  = True
iYear_data = 2006
iMon_data  = 1
iYear, iMon = [2006, 1]
eYear, eMon = [2015, 1]

#-- argv ----------------
largv = sys.argv
if len(largv)>1:
  prj, model, run, res, noleap = largv[1:1+5]
  noleap     = bool(noleap)
  iYear,iMon, eYear, eMon = map(int,largv[6:6+4])
  iYear_data, iMon_data   = map(int,largv[10:10+2])
iDTime = datetime(iYear,iMon,1,6)
eDTime = datetime(eYear,eMon,31,18)
#-------------------------


lYM    = util.ret_lYM([iYear,iMon], [eYear,eMon])
cfg    = config_func.config_func(prj, model, run)
cy     = Cyclone.Cyclone(cfg)
#**********************************************
def ret_a1initState(var, year,mon,dinitState_pre):
  #----------
  dinitState              = {}
  dinitState[-9999,-9999] = -9999.0
  #----------
  a1idate     = cy.load_clist("idate",year,mon) 
  a1ipos      = cy.load_clist("ipos" ,year,mon) 
  a1time      = cy.load_clist("time" ,year,mon) 
  a1state     = cy.load_clist(var    ,year,mon) 
  a1land      = cy.load_clist("land" ,year,mon) 

  #------------------------
  n  = len(a1idate)
  ldat    = deque([])
  for i in range(n):
    idate = a1idate[i]
    ipos  = a1ipos [i]
    time  = a1time [i]
    state = a1state[i]
    #print idate, ipos, time
    #--- check initial time --
    if time == idate:
      dinitState[idate, ipos] = state

    #-----------
    try:
      ldat.append( dinitState[idate, ipos] )
    except KeyError:
      try:
        ldat.append( dinitState_pre[idate, ipos])
      except:
        ldat.append( -9999.0)
#        sys.exit() 
  #---------------------------
  a1initState = array(ldat, float32)
  return dinitState, a1initState
#**********************************************

#--- init ----
iyear, imon= lYM[0]
date_first = datetime(iyear,imon, 1)
date_pre   = date_first + timedelta(days = -2)
year_pre   = date_pre.year
mon_pre    = date_pre.month
if (iyear == iYear_data)&(imon ==iMon_data):
  dinitsst   = {} 
  dinitland  = {} 
else:
  dinitsst , a1temp = ret_a1initState("sst" , year_pre, mon_pre, {} )
  dinitland, a1temp = ret_a1initstate("land", year_pre, mon_pre, {} )
#-------------
for [year, mon] in lYM:
  dinitsst_pre          = dinitsst
  dinitsst, a1initsst   = ret_a1initState( "sst", year, mon, dinitsst_pre )

  dinitland_pre         = dinitland
  dinitland, a1initland = ret_a1initState( "land",year, mon, dinitland_pre )
 
 
  #---- oname ----------------
  name_sst  = cy.path_clist("initsst" ,year,mon)[1]
  name_land = cy.path_clist("initland",year,mon)[1]
  a1initsst.tofile(name_sst)
  a1initland.tofile(name_land)
  print name_sst

  
