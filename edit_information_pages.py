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
        self.PICS = "No"
        self.TnC = "No"
        self.Opt_in_out = "No"
        self.remarks = ""
        self.PII = ""
        self.Label_Category_dict = {"Label": [], "Category": []}
        self.Keywords_Exist_dict = {"Keyword": ["T&C", "P.I.C.S", "Opt-in/Opt-out"], "Exist?": ["No", "No", "No"]}

    def dict_to_output(self):
        # convert Label_Category_dict to PII export item
        for categories in self.Label_Category_dict["Category"]:
            if categories != "Unrelated" and categories != "P.I.C.S" and categories != "T&C" and \
                    categories != "Opt-in/Opt-out" and categories != "Marketing Purpose" and \
                    categories != "Expiry Date" and categories != "":
                self.PII = self.PII + categories + ","
        self.PII.rstrip(",")

        # convert Keywords_Exist_dict to export items
        self.TnC = self.Keywords_Exist_dict["Exist?"][0]
        self.PICS = self.Keywords_Exist_dict["Exist?"][1]
        self.Opt_in_out = self.Keywords_Exist_dict["Exist?"][2]

    def export(self):
        export_list = [self.fb_page_name,
                       self.source,
                       self.post_time,
                       self.url,
                       self.full_url,
                       self.purpose,
                       self.status,
                       self.PICS,
                       self.TnC,
                       self.Opt_in_out,
                       self.remarks,
                       self.PII]
