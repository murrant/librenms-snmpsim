#!/usr/bin/python
import sys, re, argparse
from subprocess import check_output

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", help="The file to translate to plain oids")
parser.add_argument("-m", dest="modules", help="snmpwalk modules", action='append')
parser.add_argument("-M", dest="moddirs", help="snmpwalk directories", action='append')
args = parser.parse_args()

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
    target = target.replace('"','\\"')

    # attempt to translate the string
    out = check_output(snmpOptions + [target]).strip()
    return out


with open(args.inputfile, "r") as f:
    # set up items before looping
    number_pattern = re.compile("^([A-Za-z2346]+: )(.*\((?P<num1>-?\d+)\)|(?P<num2>-?\d+) (octets|milli-seconds|milliseconds|seconds))")
    wrong_type_pattern = re.compile("Wrong Type \(.*\): ")
    hexstring = False
    temp_oid = ""
    temp_val = ""

    for line in f:
        #skip non data lines unless we are processing a HEX-STRING
        if "=" not in line:
            if hexstring:
                temp_val += line.strip('\n')
            continue
        elif hexstring:
            print(temp_oid + ' = ' + temp_val)
            hexstring = False
            temp_oid = ""
            temp_val = ""


        parts = line.split(" =")

        # transalte oids and skip the line if the translation fails
        oid = translate(parts[0])
        if not oid:
            sys.stderr.write("Error: translation failed: " + line+ "\n")
            sys.exit(1)

        val = parts[1].strip()
        if val.startswith("OID: "):
            out = translate(val[5:])
            if not out:
                sys.stderr.write("Error: translation failed: " + line+ "\n")
                sys.exit(1)
            val = "OID: " + out

        # remove wrong type warnings
        val = wrong_type_pattern.sub('', val)

        # remove fancy formatting on numbers
        match = number_pattern.match(val)
        if match is not None:
            val = match.group(1)
            if match.group('num1') is not None:
                val += match.group('num1')
            elif match.group('num2') is not None:
                val += match.group('num2')

        if not val:
            val = '""'

        if val.startswith("Hex-STRING: "):
            hexstring = True
            temp_oid = oid
            temp_val = val
        else:
            # print out the end result
            print(oid + ' = ' + val)

