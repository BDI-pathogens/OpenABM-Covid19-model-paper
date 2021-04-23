# Script to generate TIF files that pass Plos Comp Biol submission guidelines
# 
# W. Probert, 2020
# 
# This script needs to be able to see the 'convert' function as part of Change this to the location of the 'convert' function as part of ImageMagick
#convert=convert


# Define a function that converts from PDF to TIF with the graphical parameters
# needed for submission to Plos Comp Biol.  
# 
# Note: any files built with Illustrator will need to be Saved as PDF
# File > "Save A Copy" > PDF > (Output tab) Color Conversion: Convert to Destination (Destination -> Working RGB - sRGB IEC61966-2.1

function pdf2tif {
convert -density 600 $1.pdf \
    -resize 2200 \
    -depth 8 \
    -compress lzw \
    -layers flatten \
    $1.tif
}



# Main figures
pdf2tif output/figures/figure_2_v4/fig2_v4
pdf2tif output/figures/figure_3_v1/fig3_v1
pdf2tif output/figures/fig5_ifr_by_age

# Supplementary figures
pdf2tif output/figures/figS1_I_H_D
pdf2tif output/figures/figS2_H_ICU_D
pdf2tif output/figures/figS3_waiting_time_distributions
pdf2tif output/figures/figS4_histogram_app_uptake
pdf2tif output/figures/figS13_actual_R

