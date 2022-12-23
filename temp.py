import pandas as pd
test_dict = {"Name": [],  "Link":[]}
test_dict["Name"].append("bottle")
test_dict["Link"].append({"link1.com", "link2.com"})
test_dict["Name"].append("pan")
test_dict["Link"].append({"link3.com", "link4.com"})

print(test_dict)
print("=======")
df = pd.DataFrame(test_dict)
print(df)