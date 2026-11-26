"""Stage-1 title/abstract screen (E1/E3) for the prebiotic frame. Ranks not listed in OOL are
not origin-of-life chemistry (nutrition, gut microbiome, food science, biotech 'prebiotic' fibres)."""
import csv
OOL = [0,1,5,6,7,8,10,11,13,14,15,17,19,20,22,23,24,25,28,29,30,31,32,35,36,37,40,41,42,43,45,46,47,49,51,54,55,56,57,58,59,60,61,63,64,65,68,
 70,71,73,75,79,81,82,83,84,87,88,93,94,96,100,101,102,103,107,111,112,116,117,118,123,126,129,132,133,134,138,139,140,141,142,143,146,147,148,149,151,152,153,154,155,156,157,161,162,163,165,166,168,170,172,173,174,175,176,177,178,179,181,184,186,187,189,190,191,193,195,196,198,200,201,205,207,208,209,213,214,216,218,219,221,225,227,229,230,231,232,235,236,237,238,241,243,244,245,247,248,249,251,255,258,263]
SPECIFIC = {4:"E1 no synthesis (vesicle stability)",21:"E3 ribozyme engineering, not prebiotic synthesis",26:"E1 no synthesis (condensates)",
 33:"E1 review",39:"E1 phylogenomics",44:"E1 no synthesis (vesicle assembly)",48:"E1 no synthesis (clay exfoliation)",52:"E1 account/review",
 53:"E1 review",67:"E1 computational model",72:"E1 no synthesis (membrane fluorescence)",77:"E1 model",78:"E1 review",85:"E1 review/bioinformatic",
 89:"E1 bioinformatic",90:"E1 computational",92:"E1 no synthesis (coacervates)",95:"E1 no synthesis (aerosol vesicles)",97:"E1 review",
 104:"E1 structural study",105:"E1 review",106:"E1 model",108:"E1 sample analysis (Bennu)",109:"E1 review",113:"E1 meteorite analysis",
 114:"E1 polymer physical chemistry",115:"E1 analytical method",127:"E1 ribozyme biochemistry",128:"E1 computational",130:"E1 model",
 144:"E1 hypothesis",150:"E1 no synthesis (protocell membranes)",158:"E1 no synthesis (vesicles)",160:"E1 model",180:"E1 computational",
 182:"E1 review",183:"E1 no synthesis (phase separation)",185:"E1 review/essay",188:"E1 phase separation",192:"E1 review",
 202:"E1 enzyme kinetics in protocells",206:"E1 hypothesis",210:"E1 not OoL",215:"E1 catalysis in coacervates",220:"E1 hypothesis",
 223:"E1 ribozyme network",228:"E1 protein design",234:"E1 coacervate dynamics",239:"E1 review/essay",240:"not OoL",242:"not OoL",
 250:"E1 vesicle evolution",254:"E1 computational",256:"E1 mineral analysis",257:"E1 simulation",260:"not OoL",261:"not OoL",263:"E1 model"}
rows = list(csv.DictReader(open("frame_prebiotic.csv")))
with open("stage1_prebiotic.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["rank","pmcid","stage1","reason"])
    for r in rows:
        k = int(r["rank"])
        if k in OOL and k not in SPECIFIC: w.writerow([k,r["pmcid"],"candidate",""])
        else: w.writerow([k,r["pmcid"],"excluded",SPECIFIC.get(k,"E3 not origin-of-life chemistry (nutrition/microbiome/food/biotech sense of 'prebiotic')")])
print(sum(1 for r in csv.DictReader(open("stage1_prebiotic.csv")) if r["stage1"]=="candidate"))
