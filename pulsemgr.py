#!/usr/bin/env python3
import subprocess

class PulseSink():
    "Class containing pulseaudio sink details"
    def __init__(self,name):
        self.name=name
        self.index=-1
        self.module=""
        self.sound_properties=""
        self.state="UNKNOWN"

class PulseManager:
    "Manages Pulseaudio via command line"
    def __init__(self, verbose=False):
        self._sink_list=[]
        self.verbose=verbose

    def docommand(self,cmd):
        if self.verbose:
            print(cmd)
        status,output=subprocess.getstatusoutput(cmd)
        if self.verbose:
            print("Status=",status)
            print("Output=\n",output)
        return (status,output)

    def update_sink_list(self):
        status,result=self.docommand("pactl list short sinks")
        if status==1:
            status,result=self.docommand("pulseaudio --start")
            if status==0:
                status,result=self.docommand("pactl list short sinks")
        lines=result.split("\n")
        self._sink_list=[]
        for l in lines:
            info=l.split("\t")
            if len(info)<5: continue
            sink=PulseSink(info[1])
            sink.index=int(info[0])
            sink.module=info[2]
            sink.sound_properties=info[3]
            sink.state=info[4]
            self._sink_list.append(sink)
        return self._sink_list

    def find_bluetooth(self,addr):
        """
        Find index of bluetooth device.
        addr is expected to be in the form 00:00:00:00:00:00
        returns index if found, -1 if not.
        """
        match="bluez_sink."+addr.upper().replace(":","_")
        print("Searching for...",match)
        if len(self._sink_list)<1:
            self.update_sink_list()
        for sink in self._sink_list:
            if sink.name.startswith(match):
                return sink.index
        return -1

    def set_bluetooth(self,addr):
        "Select bluetooth device as default output."
        index=self.find_bluetooth(addr)
        if (index<0):
            return False
        subprocess.call(["pactl","set-default-sink",str(index)])
        return True
    
if __name__=="__main__":
    pm=PulseManager(False)
    print("Getting list")
    ret=pm.update_sink_list()
    print("Retrieved")
    for sink in ret:
        print(sink.index,sink.name)
    print(pm.set_bluetooth("E2:8B:8E:89:6C:07"))
        
