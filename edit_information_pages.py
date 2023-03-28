from web_scrap import get_full_url

class EditInformationPage:

    def __init__(self, fb_page_name, source, post_time, url):
        """
        information saved: Brand,Source,Post Date,Link,Full True Path,Purpose,Status,PIC?,T&C?,Opt-in/Opt-out,remarks,PII
        """
        self.fb_page_name = fb_page_name
        self.source = source
        self.post_time = post_time
        self.url = url
        self.full_url = get_full_url(self.url)
        self.purpose = "Marketing Purpose"
        self.status = "Ongoing"
        self.Label_Category_dict = {"Label": [],  "Category": []}
        self.Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S", "Opt-in/Opt-out"], "Exist?": ["No", "No", "No"]}
        self.PIC = "No"
        self.TnC = "No"
        self.Opt_in_out = "No"
        self.remarks = ""
        self.PII = ""



