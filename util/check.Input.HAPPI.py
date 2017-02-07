from numpy import *
from datetime import datetime, timedelta
import myfunc.util as util
import config_func
import IO_Master
import calendar
import os, sys
##***************************
prj    = "HAPPI"
model  = "MIROC5"
expr   = "C20"
lscen  = ["P15","P20"]
#scen  = ["ALL"]
lens   = [1]
#lens   = [2,3,4,5]

dlYear = {
           "ALL":range(2006,2015+1)
          ,"P15":range(2106,2115+1)
          ,"P20":range(2106,2115+1)
         }

#verbose= True
verbose= False

ldat   = []
#ldat.append([topo","sfc","const"])  # Reads CMIP5 now
ldat.append(["ua",500,"1dy"])  # c.runmean
ldat.append(["va",500,"1dy"])  # c.runmean
ldat.append(["slp","","6hr"])  # c.findcyclone
ldat.append(["ua",850,"6hr"])  # c.findcyclone
ldat.append(["va",850,"6hr"])  # c.findcyclone
ldat.append(["sst","","mon"])  # tc.mk.tclist
ldat.append(["ta",850,"6hr"])  # tc.mk.tclist, f.mk.potloc
ldat.append(["ta",500,"6hr"])  # tc.mk.tclist
ldat.append(["ta",250,"6hr"])  # tc.mk.tclist
ldat.append(["ua",850,"6hr"])  # tc.mk.tclist
ldat.append(["ua",250,"6hr"])  # tc.mk.tclist
ldat.append(["va",850,"6hr"])  # tc.mk.tclist
ldat.append(["va",250,"6hr"])  # tc.mk.tclist
ldat.append(["prcp","","mon"])  # ms.mkRegion
ldat.append(["spfh",850,"1dy"])  # ms.FindMinMax
ldat.append(["spfh",500,"1dy"])  # ms.FindMinMax
ldat.append(["spfh",250,"1dy"])  # ms.FindMinMax
 
def ret_nz(tstp):
    if   tstp == "6hr":return 1460
    elif tstp == "1dy":return 365
    elif tstp == "mon":return 12
    else:
        print "check tstp",tstp
        sys.exit()


#******************************************
lkeys = [[scen,ens] for scen in lscen for ens in lens]
for scen, ens in lkeys:
    run    = "%s-%s-%03d"%(expr,scen,ens)
    res    = "128x256"
    print "\n"
    print "-"*50
    print run
    print "-"*50

    lYear  = dlYear[scen]
    cfg    = config_func.config_func(prj, model, run)
    iom    = IO_Master.IO_Master(prj, model, run, res)
    
    for [var,plev,tstp] in ldat:
        varName = iom.dvar[var]
        print "*"*50
        print "Check",varName, plev, tstp
        print "*"*50
    
        ny = iom.ny
        nx = iom.nx
        nz = ret_nz(tstp)
        for Year in lYear:
            srcDir  = os.path.join(iom.baseDir, model, run, "y%d"%Year, tstp)
            if type(plev) == int:
                srcPath = os.path.join(srcDir
                        ,"%s%03d.sa.%dx%dx%d"%(varName, plev, nz, ny, nx))
    
            else:
                srcPath = os.path.join(srcDir
                        ,"%s.sa.%dx%dx%d"%(varName, nz, ny, nx))
    
            checkflag= os.path.exists(srcPath)
            if verbose==True:
                if checkflag == False:
                    print "[No!]" ,varName, plev, tstp, srcPath
                else:
                    print "[   ]" ,varName, plev, tstp, srcPath
            else:
                if checkflag == False:
                    print "[No!]" ,varName, plev, tstp, srcPath
        
       
    
