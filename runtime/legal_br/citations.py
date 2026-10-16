"""Local citation candidates with exact character spans; no source authentication.

Concept: eyecite separates extraction, aggregation and annotation. This BR grammar
is original; US support is an optional adapter, not a transplanted US grammar.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from bisect import bisect_left, bisect_right
import re
from typing import Any

MAX_TEXT_BYTES = 10 * 1024 * 1024
CNJ = re.compile(r'(?<![0-9])(?P<n>[0-9]{7})-(?P<dd>[0-9]{2})\.(?P<year>[0-9]{4})\.(?P<j>[1-9])\.(?P<tr>[0-9]{2})\.(?P<origin>[0-9]{4})(?![0-9])')
ECLI_FULL = re.compile(r'ECLI:([A-Z]{2}):([A-Z][A-Z0-9]{0,6}):([0-9]{4}):([A-Z0-9.]{1,25})', re.ASCII | re.IGNORECASE)
ECLI_SCAN = re.compile(r'(?<![\w:])ECLI:[A-Za-z0-9:.]{1,100}(?![\w:])', re.ASCII | re.IGNORECASE)
STATUTE = re.compile(r'\b(?P<kind>Lei(?:\s+Complementar)?|Decreto(?:[-\s]Lei)?|Emenda\s+Constitucional|Resolu[cç][aã]o|Portaria)\s+(?:n[.º°o]*\s*)?(?P<number>[0-9]{1,6}(?:\.[0-9]{3})*)\s*/\s*(?P<year>[0-9]{4}|[0-9]{2})(?![0-9])', re.IGNORECASE)
CASE = re.compile(r'\b(?P<court>STF|STJ|TST|TSE|STM|TCU|TRF[1-6]|TJ[A-Z]{2})\s*[-–—,:]?\s*(?P<class>REsp|AREsp|ADI|ADPF|ADC|ARE|RE|HC|RHC|MS|RMS|RR|Ac[oó]rd[aã]o)\s*(?:n[.º°o]*\s*)?(?P<number>[0-9]{1,7}(?:\.[0-9]{3})*)(?:/(?P<suffix>[A-Z]{2}|[0-9]{4}))?\b', re.IGNORECASE)
SUMULA = re.compile(r'\bS[uú]mula\s+(?P<binding>Vinculante\s+)?(?:n[.º°o]*\s*)?(?P<number>[0-9]{1,4})(?:\s+(?:do\s+)?(?P<court>STF|STJ|TST|TSE|STM|TCU))?\b', re.IGNORECASE)
ARTICLE = re.compile(r'\b(?:art\.|artigo)\s*(?P<number>[0-9]{1,4})(?P<suffix>-[A-Z])?[º°]?(?:\s*,?\s*§\s*(?P<paragraph>[0-9]{1,3})[º°]?)?', re.IGNORECASE)
SHORT = re.compile(r'(?<!\w)(?:[Ii]bid\.|[Ii]bidem\b|[Ii]d\.|[Ss]upra\b)')
BIDI = re.compile('[\u202a-\u202e\u2066-\u2069]')


class IntegrationUnavailable(RuntimeError):
    """An optional installed dependency is not present; never a clean result."""


def checked_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip() or '\x00' in text:
        raise ValueError('Expected nonempty text without NUL.')
    if len(text.encode('utf-8')) > MAX_TEXT_BYTES:
        raise ValueError('Text exceeds the input budget.')
    return text


@dataclass(frozen=True)
class Citation:
    citation_id: str
    kind: str
    surface: str
    start: int
    end: int
    parts: dict[str, Any]
    syntax_status: str
    canonical_identifier: str | None = None
    existence_verified: bool = False
    semantic_support_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_cnj(value: str) -> bool:
    """CNJ Res. 65 modulo-97 check, not a lookup of a real court proceeding."""
    m = CNJ.fullmatch(value)
    if m is None:
        return False
    p = m.groupdict()
    return int(p['n'] + p['year'] + p['j'] + p['tr'] + p['origin'] + p['dd']) % 97 == 1


def parse_ecli(value: str) -> dict[str, Any]:
    if not isinstance(value, str):
        raise ValueError('ECLI must be text.')
    m = ECLI_FULL.fullmatch(value)
    if not m or set(m[4]) == {'.'} or not 1 <= int(m[3]) <= 9999:
        raise ValueError('Unsupported ECLI syntax.')
    return {'identifier':value.upper(), 'original_identifier':value, 'country':m[1].upper(), 'court':m[2].upper(), 'year':int(m[3]),
            'ordinal':m[4].upper(), 'syntax_valid':True, 'registry_verified':False,
            'existence_verified':False, 'binding_effect_verified':False}


def extract_citations(text: str) -> dict[str, Any]:
    text = checked_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    results: list[Citation] = []

    def emit(m: re.Match[str], kind: str, parts: dict[str, Any], status: str = 'recognized', identifier: str | None = None) -> None:
        if len(results) >= 50000:
            raise ValueError('Citation count budget exceeded.')
        key = f'{digest}:{m.start()}:{m.end()}:{kind}'.encode()
        results.append(Citation(hashlib.sha256(key).hexdigest(),kind,m[0],m.start(),m.end(),parts,status,identifier))

    for m in CNJ.finditer(text):
        valid = validate_cnj(m[0])
        emit(m, 'cnj_process', m.groupdict(), 'checksum_valid' if valid else 'invalid_checksum', m[0] if valid else None)
    for m in STATUTE.finditer(text):
        parts = m.groupdict(); parts['number'] = parts['number'].replace('.', '')
        parts['authority'] = None
        # Identical numbers exist at different authorities. No fabricated URN.
        emit(m, 'normative_reference', parts, 'ambiguous_year' if len(parts['year']) == 2 else 'authority_unresolved')
    for m in CASE.finditer(text):
        parts = m.groupdict(); parts['court'] = parts['court'].upper()
        parts['number'] = parts['number'].replace('.', '')
        emit(m, 'court_case_reference', parts, 'decision_identity_unresolved')
    for m in SUMULA.finditer(text):
        parts = m.groupdict(); parts['binding'] = bool(parts['binding'])
        if parts['binding'] and parts['court'] and parts['court'].upper() != 'STF':
            status = 'inconsistent_authority'
        else:
            status = 'recognized' if parts['binding'] or parts['court'] else 'authority_unresolved'
        emit(m, 'sumula_reference', parts, status)
    for m in ARTICLE.finditer(text):
        emit(m, 'provision_reference', m.groupdict(), 'parent_instrument_unresolved')
    for m in ECLI_SCAN.finditer(text):
        try:
            parts = parse_ecli(m[0])
            ambiguous = m[0].endswith('.')
            emit(m, 'ecli', parts, 'ambiguous_terminal_dot' if ambiguous else 'syntax_valid', None if ambiguous else parts['identifier'])
        except ValueError:
            emit(m, 'ecli', {}, 'invalid_or_ambiguous_syntax')
    # Indexed candidates avoid rescanning all prior citations for every Id./supra.
    antecedents = sorted((r for r in results if r.kind in {
        'court_case_reference','normative_reference','cnj_process','ecli'}), key=lambda r:r.start)
    offsets = [r.start for r in antecedents]
    paragraph_breaks = [m.end() for m in re.finditer(r'\n\n', text)]
    for m in SHORT.finditer(text):
        boundary = bisect_right(paragraph_breaks, m.start())
        paragraph_start = paragraph_breaks[boundary-1] if boundary else 0
        first = bisect_left(offsets, paragraph_start)
        last = bisect_left(offsets, m.start())
        examined = antecedents[max(first,last-128):last]
        candidates = [r.citation_id for r in examined if r.end <= m.start()]
        emit(m, 'short_reference', {'candidate_antecedents': candidates,
             'candidate_set_truncated':last-first>128}, 'requires_resolution')
    results.sort(key=lambda item:(item.start, item.end, item.kind))
    return {'schema_version':'1.0', 'engine':'legal-br-original', 'source_sha256':digest,
            'coordinate_system':'unicode_codepoints_original_text',
            'warnings':['bidirectional_controls_present'] if BIDI.search(text) else [],
            'citations':[r.to_dict() for r in results], 'external_lookup_performed':False,
            'legal_conclusion':None}


def extract_us_citations(text: str) -> dict[str, Any]:
    """Real eyecite API adapter, loaded only on explicit use. No fake fallback."""
    text = checked_text(text)
    try:
        from eyecite import get_citations
    except ImportError as exc:
        raise IntegrationUnavailable('Optional eyecite is not installed.') from exc
    found = []
    for cite in get_citations(text):
        start, end = cite.span()
        found.append({'kind':type(cite).__name__, 'start':start, 'end':end,
                      'surface':text[start:end], 'existence_verified':False})
    return {'engine':'eyecite', 'jurisdiction':'US', 'citations':found,
            'external_lookup_performed':False, 'semantic_support_verified':False}
