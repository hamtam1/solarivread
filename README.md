This Pyhton script read register from an MODBUS-TCP solar inverter Device.
The script is tested with an KACO 5.0 NX3 M2.
The inverter implements the SunSpec.

# SunSpec

The sun SunSpec Config have the "Model ID" in the first register an the "Model Lenght" in the second register. The "Model Length" describe how much bytes can be read in this model. For example in "Model 001" the can be 66 registers read (see gegister 40003).


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

# Exampe Config

The example config file implements some SunSpec Models. And some relevant registers.

# Call the script

The scipt prints its Help with the option -h.

To get the reads on stdout do:

```bash
readiv.py -H 10.10.15.38 -c modbus.json -P
```

Of course the IP must fit to your setup.