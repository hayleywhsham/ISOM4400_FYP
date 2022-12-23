import pandas as pd
link_set = {"link1.com", "link2.com"}
test_dict = {"Name": [],  "Link":[]}

for link in link_set:
    test_dict["Name"].append("bottle")
    test_dict["Link"].append(link)
print(test_dict)
print("=======")
df = pd.DataFrame(test_dict)
print(df)