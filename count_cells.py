from cv2 import cv2 # pip install opencv-python
import numpy as np
import math
import sys, getopt


"""
    constants
"""
MINIMUM_AREA = 3  # minimum area of cells
AVG_CELL_AREA = 190  # AVG size of cells
CONNECTED_CELL_AREA = 400  # minimum size of cluster of cells


def main(argv):
    """
    counts cells
        -i: input file to count
        -o: optional output file to save with highlighted contours
        -m: optional output file to save generated image mask
        -v: optional verbose flag to print cells as it counts and display generated cell mask
        -h: shows usage
    usage: count_cells.py [-h] -i <input_image> [-o <output_image>] [-m <mask_image>] [-v]

    joey aronson 2020
    """
    input_file, output_file, mask_file, verbose = parse_command_line(argv)

    # try to open picture if fails print error
    try:
        image = cv2.imread(input_file)
        highlighted = image.copy()
    except AttributeError:
        format_print("Could not read image '%s'" % input_file)
        format_print(
            "USAGE: count_cells.py -i <input_file> [-o <output_file>] [-m <mask_file] [-v]"
        )
        exit()

    # lower and upper bound of colors to accept
    hsv_lower = np.array(
        [45, 0, 50]
    )  # for hsv_lower: first num adjust higher to be less sensitive lower to be more sensitive
    hsv_upper = np.array([255, 255, 255])

    # create color mask
    mask = cv2.inRange(image, hsv_lower, hsv_upper)

    # i dont know what this stuff does, got it from https://stackoverflow.com/questions/58751101/count-number-of-cells-in-the-image
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    close = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)

    # generates list contours around shapes from the mask
    contours = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    cells = 0
    result_table = {}

    # loop through each contour
    for c in contours:
        # get area of the contour
        area = cv2.contourArea(c)

        # if cell is larger than minimum size
        if area > MINIMUM_AREA:
            # if cell is a cluster
            if area > CONNECTED_CELL_AREA:
                multi_cell = math.ceil(area / AVG_CELL_AREA)
                if verbose:
                    print(multi_cell, end=" ")
                col = (255, 0, 255)

                # keep track of sizes for results table
                if result_table.get(multi_cell):
                    result_table[multi_cell] += 1
                else:
                    result_table[multi_cell] = 1

                # add appropriate num of cells
                cells += multi_cell
            else:
                if verbose:
                    print(".", end=" ")
                col = (255, 0, 0)
                cells += 1

                # keep track of sizes for results table
                if result_table.get(1):
                    result_table[1] += 1
                else:
                    result_table[1] = 1

            # draw contour over input image
            cv2.drawContours(highlighted, [c], -1, col, 2)

    # display highlighted image
    cv2.imshow("highlighted", highlighted)

    if verbose:
        cv2.imshow("mask", mask)

    # print results talbe
    print_result_table(result_table, cells)

    # try to save image
    try:
        if output_file:
            cv2.imwrite(output_file, highlighted)
    except cv2.error:
        format_print("Could not save image, invalid output filetype (eg: test.jpg)")

    # try to save mask image
    try:
        if mask_file:
            cv2.imwrite(mask_file, mask)
    except cv2.error:
        format_print(
            "Could not save mask image, invalid output filetype (eg: test.jpg)"
        )

    # wait for user to close the image
    cv2.waitKey()


def print_result_table(res, total):
    """
    prints out the cluster counts and total cell counts into table
    """

    sorted_table = sorted(res)
    print("")
    print("")
    print("+-------------------------------+")
    print("| cluster size\t| count\t| total\t|")
    print("+-------------------------------+")
    for row in sorted_table:
        formatted_row = "| {row}\t\t| {count}\t| {total}\t|".format(
            row=row, count=res[row], total=row * res[row]
        )
        print(formatted_row)
    print("+-------------------------------+")
    print("| TOTAL\t\t\t| {total}\t|".format(total=total))
    print("+-------------------------------+")


def parse_command_line(argv):
    """
    parses command line arguments and displays usage if necessary
    """
    try:
        opts, args = getopt.getopt(argv, "hvi:o:m:")
    except getopt.GetoptError as e:
        format_print(str(e))
        format_print(
            "USAGE: count_cells.py -i <input_file> [-o <output_file>] [-m <mask_file] [-v]"
        )
        sys.exit(1)

    input_file = ""
    output_file = ""
    mask_file = ""
    verbose = False
    for opt, arg in opts:
        if opt == "-h":
            format_print(
                "USAGE: count_cells.py -i <input_file> [-o <output_file>] [-m <mask_file] [-v]"
            )
            sys.exit()
        elif opt == "-v":
            verbose = True
        elif opt == "-i":
            input_file = arg
        elif opt == "-o":
            output_file = arg
        elif opt == "-m":
            mask_file = arg

    return input_file, output_file, mask_file, verbose


def format_print(str):
    """
    formats print for errors or usage
    """
    print("")
    print("=" * len(str))
    print(str)
    print("=" * len(str))
    print("")


if __name__ == "__main__":
    main(sys.argv[1:])