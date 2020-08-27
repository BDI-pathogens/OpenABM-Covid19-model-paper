# Figures for manuscript on the OpenABM-Covid19 model


## Usage

* `step0_set_up.sh`: clone the OpenABM-Covid19 model, creates a virtual environment into which the model, and prerequisites, are installed
* `step1_run_model.sh`: runs the OpenABM-Covid19 model in a population of 1 million with demographics and control interventions similar to the UK.  Model output is stored in the `results` folder.  
* `step2_create_figures.sh`: runs python scripts to generate figures for the paper from model output




### Figure 3

Histogram of generation time of simulated transmission events stratified by infectious state of the source.  Generation time is the time from infection to transmission.  Data is from a single simulation in a population of 1 million individuals with UK-like demographics and COVID19 control interventions.  

![./figures/figure_3.png](./figures/figure_3.png)


