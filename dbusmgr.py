
import dbus

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
            
    def connect(self, address, uuid):
        "Connect to a device with address and service uuid"
        devices=self.all_devices()
        for path,dev in devices:
            properties=dev["org.bluez.Device1"]
            addr=str(properties["Address"])
            if (addr==address):
                print("Found ",path)
                devobj = self.bus.get_object('org.bluez', path)
                iface = dbus.Interface(devobj,'org.bluez.Device1')
                ret=iface.Connect()
                print("Result=",ret)
                
            
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
