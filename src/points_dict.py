points_dict = {
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
}

def new_name(id):
    return points_dict.get(id, id)

def main(input):
    name = new_name(input)
    #print(name)
    return name

if __name__ == "__main__":
    main("PM-V-3")