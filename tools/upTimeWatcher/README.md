# Watcher

## Desciption :
Watcher is a simple python application aimed to collect uptime statistic for a list of hosts for a certain port. Basically it is a simple nmap wrapper. Nmap runs for a specific list of hosts with a predefined period. Collected information stored to a log file.


## Dependencies :
 - nmap

## Usage:
Basic usage:
```
sudo ./watcher.py
```
* sudo required for nmap to enable port scanning

* feel free to use Watcher in your own applications.

## List of ip addresses:
List of ip addresses is somewhere around here. Initially, list can be very simple:
```
[
    {
        "ip": <ipAddress>
    },
    {
        "ip": <ipAddress>
    },
    .
    .
    .
]
```

## Notes:
* Nmap command to be used is hardcoded and looks as follows:
```
nmap -sS -p 3632 -oG - <ip addresses>
```
* name of `.json` file to be used is `ipList.json`.

## TODO:
* Multiple ports: for now only single port can be watched at a time.
* Make internal nmap command more flexible: for now command is hardcoded
* Add more ip addresses sources (use arguments?)