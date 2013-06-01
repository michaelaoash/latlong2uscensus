## latlong2uscensus.py
## Given US lat/long return US Census (2010) Block FIPS
## Michael Ash and Don Blair, May 2013, mash@econs.umass.edu
## With help from Ryan Acton, David Arbour, and Klara Zwickl

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


## Read comma-delimited input file with label,latitude,longitude
## Get census block fips for the lat/long from FCC
## http://www.broadbandmap.gov/developer/api/census-api-by-coordinates
## Output label, latitude, longitude, fips

# reference for requests library: http://www.python-requests.org/en/latest/user/quickstart/

# Usage:
# python latlong2uscensus.py [inputFilename] [trialNumber]
# Example:
# python latlong2uscensus.py rseqid_lat_long_sample.txt 3

import json, requests, pprint, sys

timeout=1

url = 'http://www.broadbandmap.gov/broadbandmap/census/block?'

## Read name of input file and trial number from the command line
inputFilename=str(sys.argv[1])
trialNum=int(sys.argv[2])

trialLabel = "%03d" % trialNum

outputFilename="trial_" + trialLabel + "_output.txt"
skippedFilename="trial_" + trialLabel + "_skippedLines.txt"
errorFilename="trial_" + trialLabel + "_errors.txt"

# appending to files -- make sure to change 'trialNum' above for different runs, unless you want to append results to existing files

outFile=open(outputFilename,'a') 
skippedFile=open(skippedFilename,'a')
errorFile=open(errorFilename,'a')

for line in open(inputFilename, 'r'):
    words = line.rstrip().split(',')
    if len(words)==3: 
        label=words[0]
        lat=words[1].rstrip().lstrip()
        lon=words[2].rstrip().lstrip()
        params = dict(
            latitude=lat,
            longitude=lon,
            format='json',
            showall='true'
            )
        ## Warning: may time out
        try:
            data = requests.get(url=url, params=params, timeout=timeout)
            binary = data.content
            output_json = json.loads(binary)
            ## If multiple blocks are returned they are in the 'intersect' object
            if 'intersect' in output_json['Results']:
                blocks = output_json['Results']['intersect']['block']
                for b in blocks:
                    FIPS = b['FIPS']
                    output=label+"\t"+lat+"\t"+lon+"\t"+"\t"+FIPS[0:2]+"\t"+FIPS[0:5]+"\t"+FIPS[0:11]+"\t"+FIPS[0:12]+"\t"+FIPS
                    # write to screen
                    print output
                    # write to file
                    outFile.write(output+"\n") 
            ## Otherwise block is in the 'Results' object
            else:
                blocks = output_json['Results']['block']
                for b in blocks:
                    FIPS = b['FIPS']
                    output=label+"\t"+lat+"\t"+lon+"\t"+"\t"+FIPS[0:2]+"\t"+FIPS[0:5]+"\t"+FIPS[0:11]+"\t"+FIPS[0:12]+"\t"+FIPS
                    # write to screen
                    print output
                    # write to file
                    outFile.write(output+"\n") 
        except requests.ConnectionError as e:
            #output = "\n ConnectionError:" + str(e.strerror) +", for input:" + line
            output = label + ", " + lat + ", " + lon + " -- ConnectionError\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except requests.Timeout as e:
            #output = "\n Timeout error:" + str(e.strerror) + ", for input:" + line
            output = label + ", " + lat + ", " + lon + " -- Timeout error for timeout value of " + str(timeout) + " secs\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except ValueError:
            pprint.pprint(output_json)
            output = label + ", " + lat + ", " + lon + " -- decoding JSON failed" + str(output_json['Results']) + "\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except:
            output = label + ", " + lat + ", " + lon + " -- Unexpected error\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)

outFile.close()
errorFile.close()
skippedFile.close()
