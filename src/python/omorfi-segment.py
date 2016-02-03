#!/usr/bin/env python3

from sys import stdin, stdout
from argparse import ArgumentParser
from omorfi.omorfi import Omorfi
import re

def print_segments(fmt, segments, labelsegments, surf, outfile):
    if fmt == 'labels-moses-factors':
        if float(labelsegments[0][1]) != float('inf'):
            analysis = labelsegments[0][0]
            splat = re.split("[]{}[]", analysis)
            skiptag = None
            nextsep = '|'
            moses = ''
            allow_uppers = True
            for split in splat:
                if split == '':
                    continue
                elif split in ['STUB', 'hyph?', 'XB']:
                    allow_uppers = True
                    continue
                elif split in ['SG', 'NOM', 'POS', 'ACTV', 'PRES']:
                    # we actually skip 0 morphs...?
                    allow_uppers = True
                    continue
                elif split in ['DB', 'MB', 'WB', 'wB']:
                    allow_uppers = True
                    if skiptag:
                        moses += nextsep + skiptag
                        skiptag = None
                    moses += ' '
                    nextsep = '|'
                elif split in ['NOUN', 'VERB', 'ADJ', 'COMP', 'PROPN', 'SUPER', 'AUX', 'NUM', 'PRON', 'DET']:
                    allow_uppers = True
                    skiptag = split
                elif split in ['ADV', 'ADP', 'X', 'PUNCT', 'CONJ',
                        'SCONJ', 'CONJ|VERB', 'INTJ', 'SYM']:
                    allow_uppers = True
                    moses += nextsep + split
                elif split in ['PL', 'INS', 'INE', 'ELA',
                        'ILL', 'ADE', 'ABL', 'ALL', 'ACTV', 'PASV',
                        'IMPV', 'POTN', 'COND', 'SG1', 'SG2', 'SG3', 'PL1',
                        'PL2', 'PL3', 'PAST', 'INFA', 'PAR',
                        'POSSP3', 'POSSG1', 'POSSG2', 'POSPL1', 'POSPL2',
                        'GEN', 'PCPVA', 'INFE', 'PCPMA', 'PCPNUT', 'INFMA',
                        'PE4', 'ABE', 'ESS', 'CONNEG', 'ORD', 'TRA', 'COM',
                        'INFMAISILLA', 'PCPMATON',
                        'HAN', 'KO', 'PA', 'S', 'KAAN', 'KA', 'KIN',
                        'ACC']:
                    allow_uppers = True
                    if skiptag:
                        moses += nextsep + skiptag
                        skiptag = None
                        nextsep = '.'
                    moses += nextsep + split
                    nextsep = '.'
                elif split == 'TRUNC':
                    allow_uppers = True
                    # FIXME
                    continue
                elif split.isupper():
                    if not allow_uppers and not splat[0].startswith(split):
                        print("unhandlend upper string?", split, splat)
                        exit(1)
                    else:
                        moses += split
                    allow_uppers = False
                else:
                    allow_uppers = False
                    moses += split
            if skiptag:
                moses += nextsep + skiptag
            # tweaks and hacks
            if " i " in moses or " j " in moses:
                moses = re.sub(r" ([ij]) ([a-zä]*)\|PL.", r" \1|PL \2|", moses)
            # i ne|COM
            moses = re.sub(r"i ne\|COM", "i|PL ne|COM", moses)
            moses = re.sub(r" ([a-zåäö]+) ", r" \1|NOUN ", moses)
            moses = re.sub(r"^([a-zåäö]+) ", r"\1|NOUN ", moses)
            moses = re.sub(r"([snrl])\|PCPNUTut", r"\1ut|PCPNUT", moses)
            moses = re.sub(r"([snrl])\|PCPNUTee", r"\1ee|PCPNUT", moses)
            # teh|VERB |PCPNUTdy llä|ADE
            moses = re.sub(r"\|PCPNUT([tdrsnl]?[uy])", r"\1|PCPNUT", moses)
            moses = re.sub(r"m\|PCPMA([aä])", r"m\1|PCPMA", moses)
            moses = re.sub(r"v\|PCPVA([aä])", r"v\1|PCPVA", moses)
            #puhu|VERB ma|NOUN an|INFMA.ILL
            moses = re.sub(r"(m[aä])\|NOUN ([aä]n)\|INFMA.ILL",
                    r"\1|INFMA \2|ILL", moses)
            #esitet|VERB tä|NOUN mä n|PASV.INFMA.INS
            # esitet|VERB tä|NOUN mä n|PASV.INFMA.INS
            moses = re.sub(r"(t[aä])\|NOUN (m[aä]) n\|PASV\.INFMA\.INS",
                    r"\1|PASV \2|INFMA n|INS", moses)
            #annet|VERB ta|NOUN va t|PASV.PCPVA.PL
            moses = re.sub(r"(t[aä])\|NOUN (v[aä]) t\|PASV\.PCPVA\.PL",
                    r"\1|PASV \2|PCPVA t|PL", moses)
            # todistet|VERB ta|NOUN va sti|PASV.PCPVA
            moses = re.sub(r"(t[aä])\|NOUN (v[aä]) sti\|PASV\.PCPVA",
                    r"\1|PASV \2|PCPVA sti|STI", moses)
            moses = re.sub(r"([ei])\|NOUN (n|ssa|ssä)\|INFE.", r"\1|INFE \2|", moses)
            # herättäv|VERB.PCPVAä sti
            moses = re.sub(r"v\|VERB.PCPVA([aä]) sti", r"v\1|VERB.PCPVA sti|STI", moses)
            # tarkastel|VERB ta|NOUN e ssa|PASV.INFE.INE
            moses = re.sub(r"(t[aä])\|NOUN e (ssa|ssä)\|PASV.INFE.", r"\1|PASV e|INFE \2|", moses)
            # varot|VERB ta|NOUN e n|PASV.INFE.INS
            moses = re.sub(r"(t[aä])\|NOUN e n\|PASV.INFE.", r"\1|PASV e|INFE n|", moses)
            #tä|NOUN isi in|PASV.COND.PE4
            moses = re.sub(r"t([aä])\|NOUN isi in\|PASV.COND.PE4", r"t\1|PASV isi|COND in|PE4", moses)
            # moniselitteise|ADJ sti
            moses = re.sub(r"ADJ sti$", "ADJ sti|STI", moses)
            # hillitse|VERB vä|PCPVA sti
            moses = re.sub(r"PCPVA sti$", "PCPVA sti|STI", moses)
            # valveutu|VERB nee|PCPNUT sti
            moses = re.sub(r"PCPNUT sti$", "PCPNUT sti|STI", moses)
            # ehdotta|VERB ma|PCPMA sti
            moses = re.sub(r"PCPMA sti$", "PCPMA sti|STI", moses)
            # yhdenmukaista|VERB minen
            moses = re.sub(r"\|VERB minen$", "|VERB minen|NOUN", moses)
            # mi|NOUN s 
            moses = re.sub(r"mi\|NOUN s", "mis|NOUN", moses)
            # kunnalli|ADJ s-
            moses = re.sub(r"\|(ADJ|NOUN|PROPN) s-", r"s-|\1", moses)
            # tarvin|AUX ne|NOUN |POTN.CONNEG
            moses = re.sub(r"ne\|NOUN \|POTN.CONNEG", r"ne|POTN.CONNEG", moses)
            # kiittel|VERB y
            # rauhoittel|VERB u-
            moses = re.sub(r"VERB ([uy])$", r"VERB \1|NOUN", moses)
            moses = re.sub(r"VERB ([uy]-)$", r"VERB \1|NOUN", moses)
            # clusterfuckup:
            # soveltamis|NOUN|mis|NOUN|NOUN päivä määrä|NOUN n|GEN siirtämis|NOUNs|NOUN tä|PAR
            moses = re.sub(r"mis\|NOUN\|mis\|NOUN\|NOUN ([a-zåäö]+)",
                    r"mis|NOUN \1|NOUN", moses)
            moses = re.sub(r"mis\|NOUNs\|NOUN", r"mis|NOUN", moses)
            # toimi|NOUN alo|NOUN i|NOUN ttain
            moses = re.sub(r"NOUN ttain$", "NOUN ttain|DERTTAIN", moses)
            # |X|NUM
            moses = re.sub(r"\|X\|NUM", r"X|NUM", moses)
            moses = re.sub(r"\|X-\|NUM", r"X-|NUM", moses)
            # elin|NOUN tarvike ala|NOUN
            # kehitys|NOUN yhteis|NOUN työ mis|NOUNnisteri|NOUN nä|ESS
            # ulko|NOUN maalai|NOUN s|NOUN viha mielis|ADJ tä|PAR
            # epä|NOUN tasa-arvo asia|NOUN
            moses = re.sub(r"([a-zéšäöå-]*)\|NOUN ([a-zšéäöå-]*) ([a-zšéäöå]*)\|NOUN",
                    r"\1|NOUN \2|NOUN \3|NOUN", moses)
            moses = re.sub(r"([a-zéšäöå-]*)\|NOUN ([a-zšéäöå-]*) ([a-zšéäöå]*)\|ADJ",
                    r"\1|NOUN \2|NOUN \3|ADJ", moses)
            # šakki lauda|NOUN
            # pöytä|NOUN rosé viine|NOUN i|PL stä|ELA 
            # linja-auto liikentee|NOUN n|GEN
            moses = re.sub(r"^([A-Za-z*ÉéÄŠÖÅšäöå-]*) ([a-zäöå-]*)\|NOUN",
                    r"\1|NOUN \2|NOUN", moses)
            moses = re.sub(r"^([A-Za-z*ÉéÄŠÖÅšäöå-]*) ([a-zäöå-]*)\|PROPN",
                    r"\1|PROPN \2|PROPN", moses)
            moses = re.sub(r"^\|([A-Za-z*ÉéÄŠÖÅšäöå-]*).PROPN",
                    r"\1|PROPN", moses)
            #  R|NOUN ja|ADV |S.NOUN
            # |S-.NOUN kirjaime|NOUN lla|ADE
            moses = re.sub(r"\|S.NOUN", r"S|NOUN", moses)
            moses = re.sub(r"\|S-.NOUN", r"S-|NOUN", moses)
            # |PA.NOUN
            moses = re.sub(r"\|PA.NOUN", r"PA|NOUN", moses)
            # (|PUNCT |PL.NOUN )|PUNCT
            moses = re.sub(r"^\|PL.NOUN", r"PL|NOUN", moses)
            # |NOUN |NOUN Aerospacen|UNK
            moses = re.sub(r"^\|NOUN", r"", moses)
            moses = re.sub(r" \|NOUN", r"", moses)
            print(moses, end=' ', file=outfile)
        else:
            print(surf, end='|UNK ', file=outfile)
    elif fmt == 'both-lines':
        if segments and labelsegments:
            print(segments[0][0], labelsegments[0][0], end=' ', file=outfile)
        if segments:
            print(segments[0][0], end=' ', file=outfile)
        if labelsegments:
            print(labelsegments[0][0], end=' ', file=outfile)
    else:
        print("Not implamented")
        exit(1)

def main():
    """Segment text in some formats."""
    a = ArgumentParser()
    a.add_argument('-f', '--fsa', metavar='FSAPATH',
            help="Path to directory of HFST format automata")
    a.add_argument('-i', '--input', metavar="INFILE", type=open,
            dest="infile", help="source of analysis data")
    a.add_argument('-v', '--verbose', action='store_true',
            help="print verbosely while processing")
    a.add_argument('-o', '--output', metavar="OUTFILE", 
            help="print segments into OUTFILE")
    a.add_argument('-O', '--output-format', metavar="OFORMAT", 
            help="format output suitable for OFORMAT",
            choices=["labels-tsv", "labels-moses-factors", "segments-arrows"])
    options = a.parse_args()
    omorfi = Omorfi(options.verbose)
    if options.fsa:
        if options.verbose:
            print("Reading automata dir", options.fsa)
        omorfi.load_from_dir(options.fsa, segment=True, 
                labelsegment=True)
    else:
        if options.verbose:
            print("Searching for automata everywhere...")
        omorfi.load_from_dir(labelsegment=True, segment=True)
    if options.infile:
        infile = options.infile
    else:
        infile = stdin
    if options.output:
        outfile = open(options.output, 'w')
    else:
        outfile = stdout
    if options.verbose:
        print("reading from", options.infile.name)
    if options.verbose:
        print("writign to", options.output)

    linen = 0
    for line in infile:
        line = line.strip()
        linen += 1
        if options.verbose and linen % 10000 == 0:
            print(linen, '...')
        if not line or line == '':
            continue
        surfs = omorfi.tokenise(line)
        for surf in surfs:
            segments = omorfi.segment(surf)
            labelsegments = omorfi.labelsegment(surf)
            print_segments(options.output_format, segments, labelsegments, surf, outfile)
        print(file=outfile)
    exit(0)

if __name__ == "__main__":
    main()

