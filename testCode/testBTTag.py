# Test Bluetooth TAG

#/usr/bin/env python
'''
import time
import bluetooth

xps12  = "b4:b6:76:34:50:75" # HEISEMBERG computer portatile dell XPS 12
mibandcris = "d3:37:48:24:B0:8F"

def search():
    devices = bluetooth.discover_devices(duration = 10, lookup_names = True)
    if len(devices):
        print 'trovati apparecchi bluetooth'
    else:
        print 'nessun apparecchio bluetooth trovato'
    return devices
    
while True:
    print 'ricerca'
    results = search()
    print 'fine ricerca'
    for addr, name in results:
        print 'indirizzo: '
        print addr
        print 'nome:'
        print name
    time.sleep(5)
'''

'''
import bluetooth
print "ricerca..."
nearby_devices = bluetooth.discover_devices(lookup_names = True, flush_cache = True, duration = 20)
print "trovati %d apparecchi" % len(nearby_devices)
for addr, name in nearby_devices:
    print " %s - %s" % (addr, name)
    #for services in bluetooth.find_service(address = addr):
    #    print " Name: %s" % (services["name"])
    #    print " Description: %s" % (services["description"])
    #    print " Protocol: %s" % (services["protocol"])
    #    print " Provider: %s" % (services["provider"])
    #    print " Port: %s" % (services["port"])
    #    print " Service id: %s" % (services["service-id"])
    #    print ""
    #    print ""
'''

'''
def search():
   while True:
      devices = bluetooth.discover_devices(lookup_names = True)
      for x in devices: # <--
         yield x        # <-- 
         
'''
import bluetooth
import time

target_name = "AJ-80"
target_address = None

data_sent = False

while True:
    nearby_devices = bluetooth.discover_devices()

    for bdaddr in nearby_devices:
        if target_name == bluetooth.lookup_name( bdaddr ):
            target_address = bdaddr
            break

    if (target_address is not None) and (not data_sent):
        print "ECCOTI QUA! (%s) " % target_address
        data_sent = True
    else:
        print "Non ti trovo, dove sei?"
        data_sent = False
    time.sleep(1)
