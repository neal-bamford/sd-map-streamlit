import os
import subprocess
outdir = "file://C:/DEVELOPMENT/MASTERS/semester-03/sd-map-streamlit/reports/generation/images/" # this directory has to exist..
# map.save("tmp.html")
url = "file://C:/DEVELOPMENT/MASTERS/semester-03/sd-map-streamlit/reports/generation/images/0f1740de_map_London_Barnet_Burnt_Oak_.html"
outfn = os.path.join(outdir,"_outfig.png")
subprocess.check_call(["cutycapt","--url={}".format(url), "--out={}".format(outfn)])