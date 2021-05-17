# Information on license holders (Informace o držitelích)

Find and extract data about licence holders (držitelé licencí)
from the Czech [Energy Regulatory Office website](https://www.eru.cz/licence/informace-o-drzitelich) for selected business type,
e.g. for electricity or heat production.

Few metadata like licence number, name of the holder, address, etc.

Before using --dev option download xml files manually to `samples` directory from the web.


## Usage

In your terminal type the following to install the command line app in virtual environment.

`python3 -m venv venv`

`source venv/bin/activate`

`python setup.py install`

`holders -h`

or

`python -m holders.main -h`


```
usage: holders [-h] [--dev] [--csv]
               [--business {electricity,electricity-dist,electricity-trade,heat,heat-dist,heat-trade,gas,gas-dist,gas-trade}]
               [--output FILENAME]

Retrieves data about licence holders from Energy Regulatory Office

optional arguments:
  -h, --help            show this help message and exit
  --dev                 use testig xml file from samples directory (default:
                        False)
  --csv                 export parsed data to csv (default: True)
  --business {electricity,electricity-dist,electricity-trade,heat,heat-dist,heat-trade,gas,gas-dist,gas-trade}
                        select business type: e.g. electricity or heat
                        (default: electricity)
  --output FILENAME     specify csv output filename (default: holders.csv)
```

