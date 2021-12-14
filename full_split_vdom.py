#!/usr/bin/python
# Written by Viet Le
# Feel free to use for all purposes at your own risks

# The input file name should be a good backup config from the FortiGate and must contain 'config firewall policy'

import re, os.path
import sys, getopt


#backup_file = 'D:\\Extracts\\FINAL-wyna3-fw-01_20211101_1654.conf'
# output_dir = 'D:\\Extracts\\SF\\'
# suffix_txt = '-sfda.txt'

backup_file = 'D:\\Extracts\\sfda18-fw01-cl01_20211129_1050.conf'
output_dir = 'D:\\Extracts\\SF\\'
suffix_txt = '-sf.txt'


def usage():
    """ Used to print Syntax
    """
    print("Syntax:\n\t{} -i <inputfile> -o <output_folder>".format(os.path.basename(__file__)))
    print("Examples:\n\t{} -i backup-config.conf -o OUT\\".format(os.path.basename(__file__)))

def extract_interfaces():
    """ Used to extract interfaces for each vdom
    """
    vdoms = []  # vdom list place holder

    try:
        with open(backup_file, 'r') as config_file:
            intf_block = []
            system_intf = False
            vdom_name = ''

            for command_line in config_file:
                if re.findall(r'config system interface', command_line):
                    system_intf = True
                elif system_intf:
                    intf_block.append(command_line)
                    if re.findall(r'^\s{4}next', command_line):
                        if first_intf:
                            # write the header for vdom interfaces
                            try:
                                outfile = open(output_dir + vdom_name + suffix_txt, 'w')
                                outfile.write("config global\n")
                                outfile.write("config system interface\n")
                            except IOError as e:
                                print("Output directory error: {} does not exist".format(e.strerror, output_dir))
                                usage()
                                sys.exit(2)
                        else:
                            # output file created so appending to it
                            outfile = open(output_dir + vdom_name + suffix_txt, 'a')
                        for cmd in intf_block:
                            # write interface settings to the vdom file it belongs to
                            outfile.write(cmd)
                        intf_block.clear() # clear the interface settings which were written to the output file.
                    elif re.findall(r'set vdom \".*\"', command_line):
                        vdom_name = command_line.strip(' ').strip('\n')[10:].strip('"')
                        if vdom_name not in vdoms:
                            first_intf = True
                            vdoms.append(vdom_name)
                        else:
                            first_intf = False
                    elif re.findall(r'^end', command_line):
                        system_intf = False
            for vdom in vdoms:
                outfile = open(output_dir + vdom + suffix_txt, 'a')
                outfile.write('end\n')
                outfile.write('end\n\n')
    except IOError as e:
        print("Input file error: {} or file {} is in used".format(e.strerror, backup_file))
        usage()
        sys.exit()


def main(argv):
    global backup_file
    global output_dir

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "odir="])
    except getopt.GetoptError:
        print("Error:\n\tInvalid commands")
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile"):
            backup_file = arg
        elif opt in ("-o", "--odir"):
            output_dir = arg

if __name__ == "__main__":
    main(sys.argv[1:])

    print("Please wait! I am working on {}".format(backup_file))
    print('*' * 60)
    hit = 0  # count number of vdoms were split
    vdoms = []  # vdom list place holder

    if output_dir[-1] == "\\":
        pass
    else:
        output_dir += "\\"
    if not os.path.isdir(output_dir):
        print("IO Error: Directory {} does not exist or not accessible".format(output_dir))
        usage()
        sys.exit(2)
    # extract interfaces on the same vdom to vdom file.
    extract_interfaces()

    try:
        with open(backup_file, 'r') as config_file:
            vdom_cmd = False
            for command_line in config_file:
                if re.findall(r'^next', command_line):
                    continue
                elif re.findall(r'^edit .*', command_line):
                    vdom_name = command_line.strip(' ').strip('\n')[5:]
                    if vdom_name not in vdoms:
                        vdoms.append(vdom_name)  # first time to see the vdom name which is the vdom creation block at the beginning
                    else:
                        outfile = open(output_dir + vdom_name + suffix_txt, 'a')
                        outfile.write('config vdom\n')
                        outfile.write(command_line)
                        vdom_cmd = True
                elif (vdom_cmd and not command_line == 'config vdom\n'):
                    outfile.write(command_line)
            hit = len(vdoms)
    except IOError as e:
        print("Input file error: {} or file {} does not exist.".format(e.strerror, backup_file))
        usage()
        sys.exit()
    if hit > 0:
        print("Results: {} vdoms were split to {} directory".format(int(hit), output_dir))
    else:
        print("There is no vdom in the input file {}".format(backup_file))

