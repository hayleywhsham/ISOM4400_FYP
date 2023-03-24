# link = "https://graph.facebook.com/v16.0/me?fields=id,name&access_token=EAAIOCSeJx44BANw6jt2ZAZCXPuE6fc44xXtmZACrDYIBZAppyQiYoXv8oc8OlaapTf12t1ZAI4MqjEqBVdJjk2cPKADaurNWpPd5v4VOoWURltT8RMoaPZANpfgwCI3zmS3ZB1Il61c4xcnfP1W8G0GO0coiqAa6E57J7L7ZCJTjcyNcVqm7qZAuOv8MjrVGhMJLEnuPKZBgw17hv68R5M1pMZBOKRrw35z0MSMJMETYQcNk93YgCiBaWG9"
#
# import requests
# import json
# data = json.loads(str(requests.get(link).content)[2:-1])
# print(data)
# print(data["id"])
# print(data["name"])

from facebook_scraper import get_posts

for count,post in enumerate(get_posts('nintendo', pages=999, cookies="./fbUserToken.json",)):
     print(f'Index: {count}, link:[{post["link"]}]')