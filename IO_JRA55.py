#! /usr/bin/python
from JRA55 import Jra55
from datetime import datetime, timedelta

class IO_Jra55(Jra55):
    def __init__(self, model, run, res):
        Jra55.__init__(self, res)

        self.dvar = {
                "ta"   :"tmp"
               ,"ua"   :"ugrd"
               ,"va"   :"vgrd"
               ,"slp"  :"PRMSL"
               ,"spfh" :"spfh"
               ,"prcp" :"APCP"
               ,"sst"  :"BRTMP"
               ,"topo" :"topo"
               ,"land" :"land"
               ,"pwat" :"PWAT"
               }

    def Load_6hrPlev(self, var, DTime, plev):
        Var  = self.dvar[var]
        return self.load_6hr(Var, DTime, plev)

    def Load_6hrSfc(self, var, DTime):
        Var  = self.dvar[var]
        return self.load_6hr(Var, DTime)

    def Load_monSfc(self, var, Year, Mon):
        Var  = self.dvar[var]
        return self.load_mon(Var, Year, Mon)

    def Load_monPrcp_mmd(self, Year, Mon):
        return self.load_mon_prcp_mmd(Year, Mon)

    def Load_day_spfh(self, DTime, plev, verbose=False):
        return self.time_ave(self.dvar["spfh"],DTime, DTime+timedelta(hours=23), timedelta(hours=6), lev=plev, verbose=False)


    def Load_const(self, var):
        Var  = self.dvar[var]
        return self.load_const(Var)
