
# Information about licenses

Find and extract data about licences for electricity and heat generation from the Czech [Energy Regulatory Office website](http://licence.eru.cz/) and save them to csv.

Each license has few metadata (most of them are in license holders data), can have many capacities, many facilities. Each facility can have many capacities.

The prerequisite is data about license holders (which include license id).


## Usage

In your terminal type the following to install the command line app in virtual environment.

`python3 -m venv venv`

`source venv/bin/activate`

`python setup.py install`

`licenses -h`

or

`python -m licenses.main -h`


```
usage: licenses [-h] [--dev] [--csv] [--business {electricity,heat}] [--count]
                [--start START] [--end END]

Retrieves data from licences

optional arguments:
  -h, --help            show this help message and exit
  --dev                 use downloaded html file in samples dir (default:
                        False)
  --csv                 export parsed data to csv (default: True)
  --business {electricity,heat}
                        select business type (default: electricity)
  --count               return number of licenses(default: False)
  --start START         specify start index for parsing license ids (default:
                        0)
  --end END             specify end index for parsing license ids (default:
                        None)

```


The script will export data to csv in the following structure.

```
licenses/
├── electricity
│   ├── capacities.csv
│   ├── facilities_capacities.csv
│   ├── facilities.csv
│   └── licenses.csv
└── heat
    ├── capacities.csv
    ├── facilities_capacities.csv
    ├── facilities.csv
    └── licenses.csv
```


