import os, sys
import datetime
import subprocess

dlist   = [ "dat", "cnf", "pdf", "png", "pyt", "utl", "ref", "readme", "fonts" ]
name    = "make__shimGuideMask_"

name    = name + str( datetime.date.today() ).replace( "-", "" )
com     = "tar zcvf " + name + ".tar.gz -X utl/tar_ex.conf"
for d in dlist:
    com =  com + " " + d
print( com )
subprocess.call( com.split(" ") )
