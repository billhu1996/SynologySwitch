from wakeonlan import send_magic_packet
from homeassistant.components.switch import SwitchDevice
import urllib, requests, time, random, string, logging, time
from homeassistant.const import ATTR_ENTITY_ID, CONF_HOST, CONF_NAME, CONF_TOKEN
DATA_KEY = "switch.synology"
URL = "url"
MAC = "mac"
USERNAME = "username"
PASSWORD = "password"
SECURE = "secure"
TIMEOUT = "timeout"
VERSION = "version"
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the switch from config."""

    host = config.get(CONF_HOST)
    url = config.get(URL) or ""
    mac = config.get(MAC) or ""
    username = config.get(USERNAME) or ""
    password = config.get(PASSWORD) or ""
    secure = config.get(SECURE) or False
    timeout = config.get(TIMEOUT) or 5
    version = config.get(VERSION) or 6
    if DATA_KEY not in hass.data:
        hass.data[DATA_KEY] = {}
    device = MySwitch(url, mac, username, password, secure, timeout, version)
    hass.data[DATA_KEY][host] = device
    devices = []
    devices.append(device)
    async_add_entities(devices, update_before_add=True)

class Synology:
    def __init__(self, url, mac, username, password, secure=False, timeout=5, version=6):
        self.url = url
        self.mac = mac
        self.username = username
        self.password = password
        self.secure = secure
        self.version = version
        self.timeout = timeout
        self.auth = {
            "sid": "", #session id
            "time": 0, #unix time
            "timeout": 15 * 60 #in sec
        }

    def isLoggedIn(self):
        """check if the sid is still valid"""
        return self.auth["sid"] != "" and (self.auth["time"] + self.auth["timeout"] > time.time())

    def login(self):
        """Login to your diskstation"""
        if self.isLoggedIn():
            return True
        params = urllib.parse.urlencode({
            "api": "SYNO.API.Auth",
            "method": "login",
            "version": "3",
            "account": self.username,
            "passwd": self.password,
            "session": "homebridge-synology-" + "".join(random.sample(string.ascii_lowercase, 8)),
            "format": "sid"
        })
        resp = requests.get(self.url + "/webapi/auth.cgi?" + params)
        sid = ""
        try:
            sid = resp.json()["data"]["sid"]
            self.auth["time"] = int(time.time())
        except:
            sid = ""
        #_LOGGER.error("login sid %s", sid)
        self.auth["sid"] = sid
        return sid == ""

    def shutdown(self):
        self.login()
        apiUrl = self.version >= 6 and "/webapi/entry.cgi?" or "/webapi/dsm/system.cgi?"
        params = urllib.parse.urlencode({
            "api": self.version >= 6 and "SYNO.Core.System" or "SYNO.DSM.System",
            "method": "shutdown",
            "version": "1",
            "_sid": self.auth["sid"]
        })
        #_LOGGER.error("params")
        #_LOGGER.error(params)
        resp = requests.get(self.url + apiUrl + params)
        #if resp and resp.status_code == 200 and resp.json()["success"]:
            #_LOGGER.error("shutdown OK")
        #else:
            #_LOGGER.error("shutdown fail")

    def getPowerState(self):
        try:
            resp = requests.get(self.url + "/webman/index.cgi", timeout=self.timeout)
            if resp and resp.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def wakeUp(self):
        send_magic_packet(self.mac)
        return

class MySwitch(SwitchDevice):

    def __init__(self, url, mac, username, password, secure=False, timeout=5, version=6):
        #_LOGGER.error("init %s %s %s %s %d %d %d", url, mac, username, password, secure, timeout, version)
        self._is_on = False
        self.synology = Synology(url, mac, username, password, secure, timeout, version)
        if len(mac) == 12:
            self._name = "synology" + mac
        elif len(mac) == 17:
            sep = mac[2]
            self._name = "synology" + mac.replace(sep, '')
        else:
            self._name = ""

    @property
    def should_poll(self):
        """Poll the plug."""
        return True

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return True

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the plug on."""
        self.synology.wakeUp()
        self._is_on = True

    async def async_turn_off(self, **kwargs):
        """Turn the plug off."""
        self.synology.shutdown()
        self._is_on = False

    async def async_update(self):
        """Fetch state from the device."""
        self._is_on = self.synology.getPowerState()
