#!/usr/bin/env python3
import sys, re, argparse
from subprocess import check_output

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="The file to translate to plain oids")
parser.add_argument("-m", dest="modules", help="snmpwalk modules", action='append')
parser.add_argument("-M", dest="moddirs", help="snmpwalk directories", action='append')
args = parser.parse_args()

file_format = 'snmprec'

# define the types table
snmpTypes = {
    'STRING': '4',
    'OID': '6',
    'Hex-STRING': '4x',
    'Timeticks': '67',
    'INTEGER': '2',
    'OCTET STRING': '4',
    'BITS': '4',  # not sure if this is right
    'Integer32': '2',
    'NULL': '5',
    'OBJECT IDENTIFIER': '6',
    'IpAddress': '64',
    'Counter32': '65',
    'Gauge32': '66',
    'OPAQUE': '68',
    'Counter64': '70',
    'Network Address': '4'
}

# build the base snmptranslate command
# -On number output
# -IR Random Access lookups, for mixed number and names
# -Ir Ignore range check, for invalid snmp implementations
snmpOptions = ['snmptranslate', '-On', '-IR', '-Ir']
if hasattr(args, 'moddirs') and args.moddirs is not None:
    for mod_dir in args.moddirs:
        snmpOptions.append('-M')
        snmpOptions.append(mod_dir)
if hasattr(args, 'modules') and args.modules is not None:
    for m in args.modules:
        snmpOptions.append('-m')
        snmpOptions.append(m)
# else:
#     # +ALL could cause issues with invalid mib files, but is a way to generically add mibs
#     snmpOptions.append('-m')
#     snmpOptions.append('+ALL')


# translates formatted oid to plain number
def translate(target):
    target = target.strip()
    if not target:
        return target

    # if this is already a plain number oid, return it
    oid_pattern = re.compile("[.0-9]+")
    if oid_pattern.match(target):
        return target

    # escape quotes
#    target = target.replace('"','\\"')

    # attempt to translate the string
    return check_output(snmpOptions + [target]).decode().strip()


with open(args.inputfile, "r") as f:
    # set up items before looping
    number_pattern = re.compile(
        r"^(.*\((?P<num1>-?\d+)\)|(?P<num2>-?\d+) (octets|milli-seconds|milliseconds|seconds|KBytes|Bytes))")
    wrong_type_pattern = re.compile(r"Wrong Type \(.*\): ")
    hex_string = False
    temp_oid = ""
    temp_value = ""

    for line in f:
        # skip non data lines unless we are processing a HEX-STRING
        if "=" not in line:
            if hex_string:
                temp_value += line.strip('\n')
            continue
        elif hex_string:
            if file_format == 'snmprec':
                print('{}|4x|{}'.format(temp_oid.lstrip('.'), temp_value.replace(' ', '')))
            else:
                print('{} = Hex-STRING: {}'.format(temp_oid, temp_value))
            hex_string = False
            temp_oid = ""
            temp_value = ""

        parts = line.split(" = ")

        # translate oids and skip the line if the translation fails
        oid = translate(parts[0])
        if not oid:
            sys.stderr.write("Error: translation failed: " + line + "\n")
            sys.exit(1)

        # remove wrong type warnings
        rawVal = wrong_type_pattern.sub('', parts[1].strip('\n'))

        if rawVal == "No more variables left in this MIB View (It is past the end of the MIB tree)":
            continue

        # fix mess-up in previous script
        if rawVal == '""':
            rawVal = 'STRING: '

        snmpType = False

        if ':' in rawVal:
            valParts = rawVal.split(':', 1)

            if valParts[0] in snmpTypes:
                snmpType = snmpTypes[valParts[0]]
                value = valParts[1].lstrip(' ')

                if valParts[0] == 'Network Address':
                    value = '.'.join([str(int(y, 16)) for y in value.split(':')])

        if not snmpType:
            # probably captured with -Ot
            if rawVal.isdigit():
                snmpType = '67'
            else:
                snmpType = '4'
            value = rawVal

        # translate oid types
        if snmpType == '6':
            out = translate(value)
            if not out:
                sys.stderr.write("Error: translation failed: " + line + "\n")
                sys.exit(1)
            if file_format == 'snmprec':
                value = out.lstrip('.')
            else:
                value = out

        # if snmpType == '68':
        #     sys.stderr.write("Error: translation failed: " + line + bytes.fromhex(value).decode('utf-8') + "\n")

        # remove fancy formatting on numbers
        match = number_pattern.match(value)
        if match is not None:
            if match.group('num1') is not None:
                value = match.group('num1')
            elif match.group('num2') is not None:
                value = match.group('num2')

#        if not value:
#            value = '""'

        if snmpType == '4x':
            hex_string = True
            temp_oid = oid
            temp_value = value
        else:
            # print out the end result
            if file_format == 'snmprec':
                print('{}|{}|{}'.format(oid.strip('.'), snmpType, value.strip('"')))
            else:
                print('{} = {}: {}'.format(oid, valParts[0], value))
