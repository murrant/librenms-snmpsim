#!/usr/bin/env python3
import sys, re, argparse
from subprocess import check_output

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="The file to translate to plain oids")
parser.add_argument("-m", dest="modules", help="snmpwalk modules", action='append')
parser.add_argument("-M", dest="moddirs", help="snmpwalk directories", action='append')
args = parser.parse_args()

format = 'snmprec'

# define the types table
snmpTypes    = {
    'STRING' : '4',
    'OID' : '6',
    'Hex-STRING' : '4x',
    'Timeticks' : '67',
    'INTEGER' : '2',
    'OCTET STRING' : '4',
    'BITS' : '4', # not sure if this is right
    'Integer32' : '2',
    'NULL' : '5',
    'OBJECT IDENTIFIER' : '6',
    'IpAddress' : '64',
    'Counter32' : '65',
    'Gauge32' : '66',
    'Opaque' : '68',
    'Counter64' : '70',
    'Network Address' : '4'
}

# build the base snmptranslate command
# -On number output
# -IR Random Access lookups, for mixed number and names
# -Ir Ignore range check, for invalid snmp implementations
snmpOptions = ['snmptranslate', '-On', '-IR', '-Ir']
if hasattr(args, 'moddirs') and args.moddirs is not None:
    for dir in args.moddirs:
        snmpOptions.append('-M')
        snmpOptions.append(dir)
if hasattr(args, 'modules') and args.modules is not None:
    for m in args.modules:
        snmpOptions.append('-m')
        snmpOptions.append(m)
#else:
    # +ALL could cause issues with invalid mib files, but is a way to generically add mibs
#    snmpOptions.append('-m')
#    snmpOptions.append('+ALL')


# translates formatted oid to plain number
def translate(target):
    target = target.strip()
    if not target:
        return target

    # if this is already a plain number oid, return it
    oidpat = re.compile("[\.0-9]+")
    if oidpat.match(target):
        return target

    # escape quotes
#    target = target.replace('"','\\"')

    # attempt to translate the string
    out = check_output(snmpOptions + [target]).decode().strip()
    return out


with open(args.inputfile, "r") as f:
    # set up items before looping
    number_pattern = re.compile("^(.*\((?P<num1>-?\d+)\)|(?P<num2>-?\d+) (octets|milli-seconds|milliseconds|seconds|KBytes|Bytes))")
    wrong_type_pattern = re.compile("Wrong Type \(.*\): ")
    hexstring = False
    temp_oid = ""
    temp_value = ""

    for line in f:
        #skip non data lines unless we are processing a HEX-STRING
        if "=" not in line:
            if hexstring:
                temp_value += line.strip('\n')
            continue
        elif hexstring:
            if format == 'snmprec':
                print(temp_oid.lstrip('.') + '|4x|' + temp_value.replace(' ', ''))
            else:
                print(temp_oid + ' = Hex-STRING: ' + temp_value)
            hexstring = False
            temp_oid = ""
            temp_value = ""

        #print(line.rstrip('\n'))
        parts = line.split(" = ")

        # transalte oids and skip the line if the translation fails
        oid = translate(parts[0])
        if not oid:
            sys.stderr.write("Error: translation failed: " + line+ "\n")
            sys.exit(1)

        # remove wrong type warnings
        rawVal = wrong_type_pattern.sub('', parts[1].strip('\n'))

        if rawVal == "No more variables left in this MIB View (It is past the end of the MIB tree)":
            continue

         # fix messup in previous script
        if rawVal == '""':
            rawVal = 'STRING: '

        if ':' in rawVal:
            valParts = rawVal.split(':', 1)
            snmpType = snmpTypes[valParts[0]]
            value = valParts[1].lstrip(' ')
        else:
            # probably captured with -Ot
            if rawVal.isdigit():
                snmpType = '67'
            else:
                snmpType = '4'
            value = rawVal

        if valParts[0] == 'Network Address':
            value = '.'.join([str(int(y, 16)) for y in value.split(':')])

        # translate oid types
        if snmpType == '6':
            out = translate(value)
            if not out:
                sys.stderr.write("Error: translation failed: " + line+ "\n")
                sys.exit(1)
            if format == 'snmprec':
                value = out.lstrip('.')
            else:
                value = out

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
            hexstring = True
            temp_oid = oid
            temp_value = value
        else:
            # print out the end result
            if format == 'snmprec':
                print(oid.strip('.') + '|' + snmpType + '|' + value.strip('"'))
            else:
                print(oid + ' = ' + valParts[0] + ': ' + value)
