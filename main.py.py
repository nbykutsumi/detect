import subprocess
import os, sys

prj    = "HAPPI"
model  = "MIROC5"
expr   = "C20"
#lscen  = ["P15","P20"]
#scen  = ["ALL"]
lscen  = ["P20"]

lens   = [1]
#lens   = [2,3,4,5]

dYM  = {
           "ALL":[[2006,1],[2015,12]]
          ,"P15":[[2106,1],[2115,12]]
          ,"P20":[[2106,1],[2115,12]]
         }

noleap       = True
tstp_runmean = "day"


lkeys = [[scen,ens] for scen in lscen for ens in lens]
for scen, ens in lkeys:
    run    = "%s-%s-%03d"%(expr,scen,ens)
    res    = "128x256"

    iYear,iMon = dYM[scen][0]
    eYear,eMon = dYM[scen][1]
    iYear_data = iYear
    eYear_data = eYear
    iMon_data  = 1
    iYearMinMax= iYear 
    eYearMinMax= eYear 

    cmd  = ["python","./main.py", prj, model, run, res, noleap, tstp_runmean
            ,iYear, iMon, eYear, eMon
            ,iYear_data, eYear_data
            ,iMon_data
            ,iYearMinMax, eYearMinMax
            ]

    cmd  = " ".join(map(str,cmd))
    p= subprocess.call(cmd, shell=True)
