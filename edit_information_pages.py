from web_scrap import get_full_url

class EditInformationPage:

    def __init__(self, fb_page_name, post_time, url):
        """
        information saved: Brand,Source,Post Date,Link,Full True Path,Purpose,Status,PIC?,T&C?,Opt-in/Opt-out,remarks,PII
        """
        self.fb_page_name = fb_page_name
        self.source = "Facebook"
        self.post_time = post_time
        self.url = url
        #self.full_url = get_full_url(self.url)
        self.purpose = "Marketing Purpose"
        self.status = "Ongoing"
        self.Label_Category_dict = {"Label": [],  "Category": []}
        self.Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S", "Opt-in/Opt-out"], "Exist?": ["No", "No", "No"]}
        self.PIC = "No"
        self.TnC = "No"
        self.Opt_in_out = "No"
        self.remarks = ""
        self.PII = ""

object_list = []
obj1 = EditInformationPage("hktvmall", "2/2", "http://hktvmall.com")
obj2 = EditInformationPage("nike", "3/3", "http://nike.com")
obj3 = EditInformationPage("hktvmall", "2/2", "http://hktvmall.com")
object_list.append(obj1)
object_list.append(obj2)
object_list.append(obj3)

def check_dup_links():
    full_url_list = []
    index = 0
    while index < len(object_list):
        if object_list[index].url not in full_url_list:
            full_url_list.append(object_list[index].url)
            index += 1
        else:
            del object_list[index]

check_dup_links()


