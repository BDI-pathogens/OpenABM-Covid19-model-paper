

source config.sh

rm -rf "$model_dir"
git clone https://github.com/BDI-pathogens/OpenABM-Covid19.git "$model_dir"
(cd "$model_dir"; git checkout "$release")


# Set up a virtual environment into which the model 
# and pre-reqs will be installed
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r $model_dir/tests/requirements.txt

# Install the model
(cd $model_dir/src; make clean; make)

deactivate



