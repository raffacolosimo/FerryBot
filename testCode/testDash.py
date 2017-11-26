# test Amazon Dash
from scapy.all import *

def arp_display(pkt):
    if pkt.haslayer(ARP):
        print 'arp'
        print 'richiesta. pkt[ARP].op'
        print pkt[ARP].op
        if pkt[ARP].op == 1: #who-has (request)
            print 'arp probe'
            print pkt[ARP].psrc
            #if pkt[ARP].psrc == '0.0.0.0': # ARP Probe
            if pkt[ARP].hwsrc == 'ac:63:be:84:b2:c5': # Dash NERF
                print "NERF!"
            else:
                print 'Allarme rosso!'
                print "ARP Probe da dispositivo sconosciuto: " + pkt[ARP].hwsrc 
                    
print sniff(prn=arp_display, filter="arp", store=0, count=10)
