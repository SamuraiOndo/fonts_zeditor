'''
$python ztf8.py bytes_to_id \xc3\xae
b'\xc3\xae' = 50094
$ python ztf8.py id_to_bytes 50094
50094 = b'\xc3\xae'
'''

import argparse
import codecs
import struct


def utf8_bytes_to_zouna_font_character_id(bytes):
    result = bytes[0]
    if (result & 0b10000000) == 0:
        return result
    if (result & 0b11100000) == 0b11000000:
        return (result << 8) | bytes[1]
    elif (result & 0b11110000) == 0b11100000:
        return (result << 16) | (bytes[1] << 8) | bytes[2]
    elif (result & 0b11111000) == 0b11110000:
        return (result << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3]
    return None


def font_character_id_to_zouna_utf8_bytes(id):
    int_to_four_bytes = struct.Struct('>I').pack
    bytes = int_to_four_bytes(id & 0xFFFFFFFF)
    return bytes.strip(b'\x00') or b'\x00'


def main():
    parser = argparse.ArgumentParser(
        prog='ztf-8',
        description='Work with the Zouna UTF-8 encoding')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       required=True,
                                       dest="subparser_name")

    bytes_to_id_parser = subparsers.add_parser('bytes_to_id')
    bytes_to_id_parser.add_argument(
        'bytes', type=str, help='Escaped byte string')

    id_to_bytes_parser = subparsers.add_parser('id_to_bytes')
    id_to_bytes_parser.add_argument(
        'id', type=int, help='Unsigned int that is the id')

    args = parser.parse_args()

    if args.subparser_name == 'bytes_to_id':
        bytes = codecs.escape_decode(args.bytes)[0]
        print(f'{bytes} = {utf8_bytes_to_zouna_font_character_id(bytes)}')
    else:
        id = args.id
        print(f'{id} = {font_character_id_to_zouna_utf8_bytes(id)}')


if __name__ == '__main__':
    main()
