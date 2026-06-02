import tomllib

def load_config(file_name):
    with open(file_name, "rb") as f:
        return tomllib.load(f)

def hex_to_rgb(hex: int) -> tuple[int, int, int]:
    rgb = ()
    
    for i in range(3):
        rgb = (hex & 0xFF,) + rgb
        hex >>= 8

    return rgb