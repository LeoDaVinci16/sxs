points_dict = {

    # ===============
    # VAPOR
    # ===============

    "PM-V-1": "E800",
    "PM-V-2": "Secadores",
    "PM-V-3": "PEC",
    "PM-V-4": "Nautas",
    "PM-V-5": "V800",
    "PM-V-6": "V700",
    "PM-V-7": "P400",
    "PM-V-8": "Atomitzador 1a planta",
    "PM-V-9": "Atomitzador 2a planta",
    "PM-V-10": "S600",
    "PM-V-11": "S6000",
    "STE-1": "E800",
    "STE-2": "Secadores",
    "STE-3": "PEC",
    "STE-4": "Nautas",
    "STE-5": "V800",
    "STE-6": "V700",
    "STE-7": "P400",
    "STE-8": "Atomitzador 1a planta",
    "STE-9": "Atomitzador 2a planta",
    "STE-10": "S600",
    "STE-11": "S6000",

    # ===============
    # AIGUA
    # ===============

    "E-100": "3100",
    "E-700": "3700",
    "E-800": "3800",
    "E-900": "3900",
    "P-200": "4200",
    "P-300": "4300",
    "P-400": "4400",
    "P-600": "4500",
    "L-600": "4600",
    "V-700": "4700",
    "V-800": "4800",
    "S-400B": "5400",
    "S-600": "5600",
    "S-700B": "5700",
    "S-800": "5800",
    "S-1000": "51000",
    "S-2100": "52100",
    "S-2200": "52200",
    "S-3000": "53000",
    "S-4000": "54000",
    "S-6000": "56000",
    "Y-120": "1120",
    "Y-160": "1160",
    "Y-170": "1170",
    "Y-180": "1180",
    "Y-190": "1190",
    "BV-104": "47-5",
    "BV-105": "47-1",
    "BV-106": "47-3",
    "BV-107": "47-2",
    "BV-108": "47-4",
    "BV-109": "47-6",
    "Colector": "47-7",
    "després PEC": "47-8",
    "extracció": "47-9",
    "extracció sud/nord": "47-10",
}

def new_name(id):
    return points_dict.get(id, id)

def main(input):
    name = new_name(input)
    print(name)
    return name

if __name__ == "__main__":
    main("PM-V-3")