# fortigate-vdom-split
A Python script to split all vdoms to separate config file. It's useful for comparing config revision at vdom level.

When run directly from IDE (I am using IntelliJ IDEA) edit the following directives for input file, output directory and vdom filename suffix.
The file system is Windows.

backup_file = 'D:\\Extracts\\sfda18-fw01-cl01_20211129_1050.conf'
output_dir = 'D:\\Extracts\\SF\\'
suffix_txt = '-sf.txt'
