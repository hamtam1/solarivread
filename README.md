This Python script reads register from an MODBUS-TCP solar inverter Device.
The script is tested with an KACO 5.0 NX3 M2.
The inverter implements the SunSpec.

# SunSpec

The sun SunSpec Config have the "Model ID" in the first register an the "Model Lenght" in the second register. The "Model Length" describe how much bytes can be read in this model. For example in "Model 001" the can be 66 registers read (see register 40003).


## Register config file

The registers which should get read are configured in an json file.
The following exaple shows how to read the manufacturer String.
Registers get read, if the parameter `read` is `true`.
The format can be one of `string`, `acc32`, `sunssf`, `int16` or `uint16`.

```json
{
  "40004": {
    "Description": "Manufacturer",
    "Format": "string",
    "Size": 16,
    "Unit": "-",
    "read": true
  },
}
``` 

# Example Config

The example config file implements some SunSpec Models. And some relevant registers.

# Call the script

The script prints its Help with the option -h.

To get the reads on stdout do:

```bash
readiv.py -H 10.10.15.38 -c modbus.json -P
```

Of course the IP must fit to your setup.

# Example for Home Assistant

To use the values with home assistant, the output can be written to the web folder:
```
/usr/local/bin/readKACO.py -H 10.10.15.38 -o /var/www/html/data/kako.json
```
It you call it without -c, the script looks for an configuration in `/etc/kaco/modbus.json`.

To get the values up to date the script can get calls via chron:

```
*/1 * * * * /usr/local/bin/readiv.py -H 10.10.15.38 -o /var/www/html/data/kako.json
```

Here is a `configuration.yaml` sniped for Home Assistant:

```yaml
sensor:
  - platform: rest
    name: "Netzfrequenz"
    device_class: 'frequency'
    state_class: 'measurement'
    unit_of_measurement: "Hz"
    scan_interval: 60
    resource: http://localhost/data/kako.json
    value_template: >
      {{ value_json["40086"].Value / 100 }}
    method: GET
    verify_ssl: false

```

# Note

The inverter sends only values when it is working. You will not get an answer during the night. It does not even answer on ping.
You should therefore carry out your tests during the day when the solar system is supplying energy.
