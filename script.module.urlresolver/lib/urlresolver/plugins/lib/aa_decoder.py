# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for openload.io
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------
# Modified by Shani
import re
from urlresolver import common


class AADecoder(object):

    def __init__(self, aa_encoded_data):
        self.encoded_str = aa_encoded_data.replace('/*´∇｀*/', '')
        self.b = ["(c^_^o)", "(ﾟΘﾟ)", "((o^_^o) - (ﾟΘﾟ))", "(o^_^o)",
                  "(ﾟｰﾟ)", "((ﾟｰﾟ) + (ﾟΘﾟ))", "((o^_^o) +(o^_^o))", "((ﾟｰﾟ) + (o^_^o))",
                  "((ﾟｰﾟ) + (ﾟｰﾟ))", "((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "(ﾟДﾟ) .ﾟωﾟﾉ", "(ﾟДﾟ) .ﾟΘﾟﾉ",
                  "(ﾟДﾟ) ['c']", "(ﾟДﾟ) .ﾟｰﾟﾉ", "(ﾟДﾟ) .ﾟДﾟﾉ", "(ﾟДﾟ) [ﾟΘﾟ]"]

    def is_aaencoded(self):
        idx = self.encoded_str.find("ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); ")
        if idx == -1:
            return False

        is_encoded = self.encoded_str.find("(ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');", idx) != -1
        return is_encoded

    def base_repr(self, number, base=2, padding=0):
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if base > len(digits):
            base = len(digits)

        num = abs(number)
        res = []
        while num:
            res.append(digits[num % base])
            num //= base
        if padding:
            res.append('0' * padding)
        if number < 0:
            res.append('-')
        return ''.join(reversed(res or '0'))

    def decode_char(self, enc_char):
        end_char = "+ "
        str_char = ""
        while enc_char != '':
            found = False

            if not found:
                for i in range(len(self.b)):             
                    enc_char = enc_char.replace(self.b[i], str(i))

                startpos = 0
                findClose = True
                balance = 1
                result = []
                if enc_char.startswith('('):
                    l = 0

                    for t in enc_char[1:]:
                        l += 1
                        if findClose and t == ')':
                            balance -= 1
                            if balance == 0:
                                result += [enc_char[startpos:l + 1]]
                                findClose = False
                                continue
                        elif not findClose and t == '(':
                            startpos = l
                            findClose = True
                            balance = 1
                            continue
                        elif t == '(':
                            balance += 1

                if result is None or len(result) == 0:
                    return ""
                else:
                    for r in result:
                        value = self.decode_digit(r)
                        str_char += value
                        if value == "":
                            return value

                    return str_char

            enc_char = enc_char[len(end_char):]

        return str_char

    def parseJSString(self, s):
        try:
            tmp = (s.replace('!+[]','1').replace('!![]','1').replace('[]','0'))  # .replace('(','str(')[offset:])
            val = int(eval(tmp))
            return val
        except:
            pass

    def decode_digit(self, enc_int):
        rerr = enc_int.split('))+')
        v = ""
        for c in rerr:
            if len(c) > 0:
                if c.strip().endswith('+'):
                    c = c.strip()[:-1]
                startbrackets = len(c) - len(c.replace('(', ''))
                endbrackets = len(c) - len(c.replace(')', ''))
                if startbrackets > endbrackets:
                    c += ')' * (startbrackets - endbrackets)
                if '[' in c:
                    v += str(self.parseJSString(c))
                else:
                    v += str(eval(c))
        return v

    def decode(self):
        self.encoded_str = re.sub('^\s+|\s+$', '', self.encoded_str)

        pattern = (r"\(ﾟДﾟ\)\[ﾟoﾟ\]\+ (.+?)\(ﾟДﾟ\)\[ﾟoﾟ\]\)")
        result = re.search(pattern, self.encoded_str, re.DOTALL)
        if result is None:
            common.log_utils.log_debug("AADecoder: data not found")
            return False

        data = result.group(1)

        begin_char = "(ﾟДﾟ)[ﾟεﾟ]+"
        alt_char = "(oﾟｰﾟo)+ "

        out = ''
        while data != '':
            if data.find(begin_char) != 0:
                common.log_utils.log_debug("AADecoder: data not found")
                return False

            data = data[len(begin_char):]

            enc_char = ""
            if data.find(begin_char) == -1:
                enc_char = data
                data = ""
            else:
                enc_char = data[:data.find(begin_char)]
                data = data[len(enc_char):]

            radix = 8
            if enc_char.find(alt_char) == 0:
                enc_char = enc_char[len(alt_char):]
                radix = 16

            str_char = self.decode_char(enc_char)

            if str_char == "":
                common.log_utils.log_debug("no match :  ")
                common.log_utils.log_debug(data + "\nout = " + out + "\n")
                return False
            out += chr(int(str_char, radix))

        if out == "":
            common.log_utils.log_debug("no match : " + data)
            return False

        return out
