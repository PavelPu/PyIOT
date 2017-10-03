import json

rs = "off"



prop = {
    "relays" : {
        "dining": rs}
    }
print(prop)

js = json.dumps(prop)

print(js)