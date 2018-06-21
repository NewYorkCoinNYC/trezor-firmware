#!/usr/bin/env python2
import json
import os

import collections

HEADER_TEMPLATE = """
// This file is automatically generated by coin_info.py -- DO NOT EDIT!

#ifndef __COIN_INFO_H__
#define __COIN_INFO_H__

#include "coins.h"

#define COINS_COUNT ({count})

extern const CoinInfo coins[COINS_COUNT];

#endif
""".lstrip()

CODE_TEMPLATE = """
// This file is automatically generated by coin_info.py -- DO NOT EDIT!

#include "coins.h"

#include "curves.h"
#include "secp256k1.h"

const CoinInfo coins[COINS_COUNT] = {{
{coins}
}};
""".lstrip()


def format_bool(value):
    if value:
        return "true"
    else:
        return "false"


def format_number(value):
    if value is None:
        value = 0
    return str(value)


def format_string(value):
    if value is None:
        return "NULL"
    else:
        return json.dumps(value)


def format_hex(value):
    if value is None:
        value = 0
    return "0x{:08x}".format(value)


def prepend_varint(string):
    assert len(string) < 253

    varint = "\"\\x{:02x}\"".format(len(string))
    return "{} {}".format(varint, format_string(string))


def coin_to_struct(coin):
    return collections.OrderedDict((
        ("coin_name",             format_string(coin["coin_name"])),
        ("coin_shortcut",         format_string(" " + coin["coin_shortcut"])),
        ("maxfee_kb",             format_number(coin["maxfee_kb"])),
        ("signed_message_header", prepend_varint(coin["signed_message_header"])),              # noqa: E501
        ("has_address_type",      format_bool(coin["address_type"] is not None)),              # noqa: E501
        ("has_address_type_p2sh", format_bool(coin["address_type_p2sh"] is not None)),         # noqa: E501
        ("has_segwit",            format_bool(coin["segwit"])),
        ("has_fork_id",           format_bool(coin["fork_id"] is not None)),
        ("force_bip143",          format_bool(coin["force_bip143"])),
        ("decred",                format_bool(coin["decred"])),
        ("address_type",          format_number(coin["address_type"])),
        ("address_type_p2sh",     format_number(coin["address_type_p2sh"])),
        ("xpub_magic",            format_hex(coin["xpub_magic"])),
        ("xprv_magic",            format_hex(coin["xprv_magic"])),
        ("fork_id",               format_number(coin["fork_id"])),
        ("version_group_id",      format_hex(coin["version_group_id"])),
        ("bech32_prefix",         format_string(coin["bech32_prefix"])),
        ("cashaddr_prefix",       format_string(coin["cashaddr_prefix"])),
        ("coin_type",             "({} | 0x80000000)".format(format_number(coin["slip44"]))),  # noqa: E501
        ("curve_name",            "{}_NAME".format(coin["curve_name"].upper())),               # noqa: E501
        ("curve",                 "&{}_info".format(coin["curve_name"])),
    ))


def format_struct(struct):
    return "{\n" + "\n".join(
        "\t.{0} = {1},".format(member, value)
        for member, value in struct.items()
    ) + "\n}"


def format_coin(coin):
    return format_struct(coin_to_struct(coin))


def format_coins(coins):
    return "\n".join("{},".format(format_coin(coin)) for coin in coins)


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    coins = []

    support = json.load(open('defs/support.json', 'r'), object_pairs_hook=collections.OrderedDict)
    defs = support['trezor1'].keys()

    for c in defs:
        name = c.replace(' ', '_').lower()
        if name == 'testnet':
            name = 'bitcoin_testnet'
        data = json.load(open('defs/coins/%s.json' % name, 'r'))
        coins.append(data)

    with open("coin_info.h", "w+") as f:
        f.write(HEADER_TEMPLATE.format(count=len(coins)))

    with open("coin_info.c", "w+") as f:
        f.write(CODE_TEMPLATE.format(coins=format_coins(coins)))
