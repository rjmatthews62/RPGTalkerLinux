#!/usr/bin/python3

from __future__ import absolute_import, print_function, unicode_literals

from gi.repository import GObject

import dbus
import dbus.mainloop.glib
import threading

relevant_ifaces = [ "org.bluez.Adapter1", "org.bluez.Device1" ]

def property_changed(interface, changed, invalidated, path):
    iface = interface[interface.rfind(".") + 1:]
    for name, value in changed.items():
        val = str(value)
        print("{%s.PropertyChanged} [%s] %s = %s" % (iface, path, name,
                                    val))

def interfaces_added(path, interfaces):
    for iface, props in interfaces.items():
        if not(iface in relevant_ifaces):
            continue
        print("{Added %s} [%s]" % (iface, path))
        for name, value in props.items():
            print("      %s = %s" % (name, value))

def interfaces_removed(path, interfaces):
    for iface in interfaces:
        if not(iface in relevant_ifaces):
            continue
        print("{Removed %s} [%s]" % (iface, path))

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    bus.add_signal_receiver(property_changed, bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.Properties",
            signal_name="PropertiesChanged",
            path_keyword="path")

    bus.add_signal_receiver(interfaces_added, bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesAdded")

    bus.add_signal_receiver(interfaces_removed, bus_name="org.bluez",
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesRemoved")

    mainloop = GObject.MainLoop()
    t=threading.Thread(target=mainloop.run)
    t.start()
    print("Monitoring...")
    input("Hit enter to exit.")
    mainloop.quit()
    t.join() # Wait for thread to finish.
    print("Done")
    
    

