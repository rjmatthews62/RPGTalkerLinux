import dbus

SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"

class DbusManager:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                    "org.freedesktop.DBus.ObjectManager")

    def extract_objects(self,object_list):
        list = ""
        for object in object_list:
            val = str(object)
            list = list + val[val.rfind("/") + 1:] + " "
        return list

    def extract_uuids(self,uuid_list):
        list = ""
        for uuid in uuid_list:
            if (uuid.endswith("-0000-1000-8000-00805f9b34fb")):
                if (uuid.startswith("0000")):
                    val = "0x" + uuid[4:8]
                else:
                     val = "0x" + uuid[0:8]
            else:
                     val = str(uuid)
            list = list + val + " "
        return list

    def objects(self):
        "Return the full list of managed objects"
        return self.manager.GetManagedObjects()

        
    def all_device_names(self):
        "Return a list of all known bluetooth device paths."
        objects = self.manager.GetManagedObjects()
        return (str(path) for path, interfaces in objects.items() if
                            "org.bluez.Device1" in interfaces.keys())
        
    def all_devices(self):
        "Return a list of all known bluetooth devices."
        objects = self.manager.GetManagedObjects()
        return ((str(path),interfaces) for path, interfaces in objects.items() if
                            "org.bluez.Device1" in interfaces.keys())
        
    def all_adapters(self):
        "Return a list of all bluetooth adaptors"
        objects=self.objects()
        return ((str(path),interfaces) for path, interfaces in objects.items() if
                            "org.bluez.Adapter1" in interfaces.keys())
    def friendly_names(self):
        "Get a list of all devices tagged with the friendly name"
        result={}
        objects=self.objects()
        for path,interfaces in self.all_devices():
            properties=interfaces["org.bluez.Device1"]
            name=str(properties["Alias"])
            address=str(properties["Address"])
            result[name]=address
        return result
            
    def device_properties(self):
        "Return list of properties for all BT devices"
        result={}
        for path,interfaces in self.all_devices():
            properties=interfaces["org.bluez.Device1"]
            result[properties["Address"]]=properties
        return result
                   
    def connect(self, address, uuid):
        "Connect to a device with address and service uuid"
        try:
            self.find_device(address)
        except Exception as err:
            print("Exception=",err)
            return
        devices=self.all_devices()
        for path,dev in devices:
            properties=dev["org.bluez.Device1"]
            addr=str(properties["Address"])
            if (addr==address):
                print("Found ",path)
                devobj = self.bus.get_object('org.bluez', path)
                iface = dbus.Interface(devobj,'org.bluez.Device1')
                try:
                    ret=iface.Connect()
                    print("Result=",ret)
                except Exception as err:
                    print("Exception=",err)
                  
    def disconnect(self,address):
        "Disconnect selected bluetooth device."
        iface=self.find_device(address)
        print("Disconnecting")
        iface.Disconnect()
        print("Disconnect done.")
        
    def find_adapter(self,pattern=None):
        return self.find_adapter_in_objects(self.objects(), pattern)

    def find_adapter_in_objects(self,objects, pattern=None):
        bus = dbus.SystemBus()
        for path, ifaces in objects.items():
            adapter = ifaces.get(ADAPTER_INTERFACE)
            if adapter is None:
                continue
            if not pattern or pattern == adapter["Address"] or \
                                path.endswith(pattern):
                obj = bus.get_object(SERVICE_NAME, path)
                return dbus.Interface(obj, ADAPTER_INTERFACE)
        raise Exception("Bluetooth adapter not found")

    def find_device(self, device_address, adapter_pattern=None):
        return self.find_device_in_objects(self.objects(), device_address,
                                        adapter_pattern)

    def find_device_in_objects(self,objects, device_address, adapter_pattern=None):
        bus = dbus.SystemBus()
        path_prefix = ""
        if adapter_pattern:
            adapter = find_adapter_in_objects(objects, adapter_pattern)
            path_prefix = adapter.object_path
        for path, ifaces in objects.items():
            device = ifaces.get(DEVICE_INTERFACE)
            if device is None:
                continue
            if (device["Address"] == device_address and
                            path.startswith(path_prefix)):
                obj = bus.get_object(SERVICE_NAME, path)
                return dbus.Interface(obj, DEVICE_INTERFACE)

        raise Exception("Bluetooth device not found")


    def printlist(self):
        "Print detailed list of devices"
        objects = self.manager.GetManagedObjects()
        print("Objects found=",len(objects))
        all_devices=self.all_device_names()
        
        for path, interfaces in self.all_adapters():
            print("[ " + path + " ]")

            properties = interfaces["org.bluez.Adapter1"]
            for key in properties.keys():
                value = properties[key]
                if (key == "UUIDs"):
                    list = self.extract_uuids(value)
                    print("    %s = %s" % (key, list))
                else:
                    print("    %s = %s" % (key, value))

            device_list = [d for d in all_devices if d.startswith(path + "/")]

            for dev_path in device_list:
                print("    [ " + dev_path + " ]")

                dev = objects[dev_path]
                properties = dev["org.bluez.Device1"]

                for key in properties.keys():
                    value = properties[key]
                    if (key == "UUIDs"):
                        list = self.extract_uuids(value)
                        print("        %s = %s" % (key, list))
                    elif (key == "Class"):
                        print("        %s = 0x%06x" % (key, value))
                    elif (key == "Vendor"):
                        print("        %s = 0x%04x" % (key, value))
                    elif (key == "Product"):
                        print("        %s = 0x%04x" % (key, value))
                    elif (key == "Version"):
                        print("        %s = 0x%04x" % (key, value))
                    else:
                        print("        %s = %s" % (key, value))
            print("")


if __name__=="__main__":
    mgr=DbusManager()
    mgr.printlist()
