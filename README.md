# librenms-snmpsim
snmpwalk and snmprec files for simulating devices

## Using

### Add localhost aliases
Edit your `/etc/hosts` file
```
127.0.0.1 localhost snmpsim
```
You may add more if you would like to add multiple test devices to LibreNMS.

### Start snmpsim
Use the provided script
```
./snmpsim.sh
```

Or run by hand
```
snmpsimd.py --data-dir=./captures --agent-udpv4-endpoint=127.0.0.1:1161
```

### Add a new host to LibreNMS
Use either the command line or the webui to add a new host to LibreNMS.

Hostname: snmpsim (or anything you added to hosts)
Community: <The name of the file you want to simulate>


```
./addhost.php snmpsim ucd v2c 1161

```


### Changing the simulated device

You may either remove then re-add the device or simply change the SNMP community string.
Re-run discovery and poller.
