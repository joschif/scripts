import random
import argparse

# Parse script parameters
def interface():

    parser = argparse.ArgumentParser(description='Script to generate dissimilar colors.')
    parser.add_argument('-n', '--number',
                        dest='n',
                        type=int,
                        default='10',
                        help='Number of colors to generate.')

    parser.add_argument('-r', '--reproducible',
                        dest='reproducible',
                        action='store_true',
                        help='Make colors reproducible.')

    parser.add_argument('-p', '--previous',
                        dest='previous',
                        type=str,
                        nargs='+',
                        help='Previous colors.')

    parser.add_argument('-f', '--pastel-factor',
                        dest='pastel',
                        type=float,
                        default='0.5',
                        help='Pastel factor.')

    args = parser.parse_args()
    return args

def get_random_color(pastel_factor = 0.5):
    return [(x+pastel_factor)/(1.0+pastel_factor) for x in (random.uniform(0,1.0) for i in range(3))]

def color_distance(c1,c2):
    return sum([abs(x[0]-x[1]) for x in zip(c1,c2)])

def generate_new_color(existing_colors, pastel_factor = 0.5):
    max_distance = None
    best_color = None
    for i in range(0, 200):
        color = get_random_color(pastel_factor = pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color

def perc_to_rgb(perc_color):
    return tuple(int(n * 255) for n in perc_color)

def rgb_to_perc(rgb_color):
    return tuple(float(n / 255) for n in rgb_color)

def rgb_to_hex(rgb_color):
    r, g, b = rgb_color
    return "#{0:02x}{1:02x}{2:02x}".format(r, g, b)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    return tuple(int(hex_color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

#Example:

if __name__ == '__main__':
    args = interface()

    if args.reproducible:
        random.seed(10)

    if args.previous:
        colors = [rgb_to_perc(hex_to_rgb(c)) for c in args.previous]
    else:
        colors = []

    for i in range(0, args.n):
      colors.append(generate_new_color(colors, pastel_factor = args.pastel))

    rgb = [perc_to_rgb(c) for c in colors]
    hx = [rgb_to_hex(c) for c in rgb]

    print(colors)
    print(rgb)
    print(hx)
