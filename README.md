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

### systemd fanciness
Using systemd, we can automatically start snmpsimd.py whenever a connection is started to udp:1161
and restart it whenever a capture file is changed, added, or removed.

Copy the systemd files to /etc/systemd/system
```
cp scripts/systemd/* /etc/systemd/system/
```
Edit snmpsimd.service and snmpsim-watch.path and put in the correct paths and user.

Enable and start the proper units:
```
systemctl enable --now snmpsimd.socket snmpsim-watch.path
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


## Adding captures

See the snmpsim documentation about capture snmprec files.


`translate-snmpwalk.py` is provide to convert user provide snmpwalks to a usable file format.
