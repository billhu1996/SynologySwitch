# SynologySwitch
Synology switch for Home Assistant. Control your Synology Diskstation with Home Assistant.

>supports DSM 5.x and 6.x

## How to use

Install Home Assistant first.

### 1

Using [Home Assistant Community Store](https://hacs.xyz/)

OR

Copy `__init__.py` and `switch.py` to `homeassistant/custom_components/synology_switch/`

### 2

Edit `configuration.yaml`

Example:

```
switch:
  - platform: synology_switch
    url: https://www.example.com:5001
    mac: 00:11:22:33:EE:FF
    username: username
    password: pass
    secure: False
```

- url

    https://www.example.com:5001

    http://192.168.1.2:5000
    
    https://192.168.1.2:5001
    
## Functions

- wake up (wake-on-lan has to be active) your diskstation
- shutdown your diskstation

## Issues

Please double check your config.json before opening an issue.
When you open an issue provide a detailed description of your problem and add your config.json (without password).

## Support

PRs are always welcome.

## Thanks

[Homebridge-Synology](https://github.com/stfnhmplr/homebridge-synology)

