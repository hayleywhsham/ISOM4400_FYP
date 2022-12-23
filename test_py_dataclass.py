import datetime
from dataclasses import dataclass, field

@dataclass
class MarkWeb:
    brand: str
    source: str #= field(default="FB")
    post_datetime: datetime.datetime
    short_link: str
    full_link: str


def main() -> None:
    mark_web = MarkWeb(brand="hktvmall", source="Facebook", \
                       post_datetime= "2022-12-23 16:30:50", \
                       short_link="https://bit.ly/3GaLReF", \
                       full_link="https://bit.ly/3GaLReF")
    print(mark_web)

if __name__ == "__main__":
    main()