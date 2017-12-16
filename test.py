
str = "TEMP+10"
str2 = "TEMP-9"

print(int(str[str.find("+")+1:]))
print(str2.find("+"))

#import json

#rs = "off"



#prop = {
#    "relays" : {
#        "dining": {
#            "state":rs},
#        "bath" : {
#            "state":"on"}
#        }
#    }
#print(prop)

#rooms = ["dining", "bath"]

#js = json.dumps(prop)

#for i in prop["relays"]:
#    print(prop["relays"][i]["state"])


#print(js)

#print(prop["relays"]["dining"])