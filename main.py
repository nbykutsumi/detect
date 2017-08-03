import subprocess
import os, sys

#prj     = "JRA55"
#model   = "__"
#run     = "__"
#res     = "145x288"
#noleap  = False
#tstp_runmean = "6hr"

#prj     = "HAPPI"
#model   = "MIROC5"
##run     = "C20-P15-001"
##run     = "C20-ALL-001"
#expr    = "C20"
#lscen   = ["P15","P20"]
##lscen   = ["P20"]
##lens    = [11,21,31,41]
##lens    = [21]
#lens    = [31,41]
#lrun    = ["%s-%s-%03d"%(expr,scen,ens)
#            for scen in lscen
#            for ens  in lens]
##lrun.remove("C20-P15-021")
#print lrun
#
#res     = "128x256"
#noleap  = True
#tstp_runmean = "day"
#
#iYear, iMon = [2106,1]
#eYear, eMon = [2115,12]
#iYear_data  = 2106
#eYear_data  = 2115
#iMon_data   = 1
#
##iYear, iMon = [2006,1]
##eYear, eMon = [2015,12]
##iYear_data  = 2006
##eYear_data  = 2015
##iMon_data   = 1
#
##iYear, iMon = [2006,1]
##eYear, eMon = [2014,12]  # JRA55
##iYear_data  = 2006
##eYear_data  = 2014
##iMon_data   = 1
#
#
#iYearMinMax = iYear_data
#eYearMinMax = eYear_data

#------------------------------
largv = sys.argv
if len(largv)>1:
    print largv
    prj, model, run, res, noleap, tstp_runmean = largv[1:1+6]
    iYear, iMon, eYear, eMon  = largv[7:7+4]
    iYear_data, eYear_data    = largv[11:11+2]
    iMon_data                 = largv[13]
    iYearMinMax, eYearMinMax  = largv[14:14+2]

lrun   = [run] 
#logDir = "~/log"
logDir = "/home/utsumi/log"
#*********************************
def exec_func(cmd):
    cmd = " ".join(map(str, cmd))
    print cmd
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    stdout_data, stderr_data = p.communicate()
    p.wait()
    print stderr_data

    prog       = cmd.split(" ")[1][:-3]
    stdoutPath = logDir +"/stdout.%s.%s.%s.%s.txt"%(prj,model,run, prog)
    stderrPath = logDir +"/stderr.%s.%s.%s.%s.txt"%(prj,model,run, prog)

    f=open(stdoutPath, "w"); f.write(stdout_data); f.close()
    f=open(stderrPath, "w"); f.write(stderr_data); f.close()


#*********************************
# START LOOP
#---------------------------------
for run in lrun:
    print '*'*50
    print 'run=',run
    print '*'*50
    #*********************************
    # Preparation
    #---------------------------------
    cmd = ["python","prep.py"
            , prj, model, run, res
        ]
    exec_func(cmd)
         
    #*********************************
    # Cyclone (ExC and TC)
    #---------------------------------
    cmd = ["python","c.runmean.wind.py"
            , prj, model, run, res, tstp_runmean, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    cmd = ["python","c.findcyclone.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    cmd = ["python","c.connectc.fwd.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    flagresume = False
    cmd = ["python","c.connectc.bwd.py"
            , prj, model, run, res, noleap, flagresume
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    cmd = ["python","c.mk.clist.obj.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    #*********************************
    # Cyclone (TC)
    #---------------------------------
    cmd = ["python","tc.mk.clist.obj.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    cmd = ["python","tc.mk.clist.obj.initState.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
            , iYear_data, iMon_data
        ]
    exec_func(cmd)
    
    #*********************************
    # Front
    #---------------------------------
    cmd = ["python","f.mk.orogdata.py"
            , prj, model, run, res
        ]
    exec_func(cmd)
    
    cmd = ["python","f.mk.potloc.obj.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
        ]
    exec_func(cmd)
    
    #*********************************
    # Monsoon
    #---------------------------------
    cmd = ["python","ms.mkRegion.py"
            , prj, model, run, res, noleap
            , iYear_data, eYear_data
        ]
    exec_func(cmd)
    
    cmd = ["python","ms.FindMinMax.py"
            , prj, model, run, res, noleap
            , iYearMinMax, eYearMinMax
        ]
    exec_func(cmd)
    
    cmd = ["python","ms.mkMonsoon.py"
            , prj, model, run, res, noleap
            , iYear, iMon, eYear, eMon
            , iYearMinMax, eYearMinMax
            , iYear_data,  eYear_data
        ]
    exec_func(cmd)
    
    
