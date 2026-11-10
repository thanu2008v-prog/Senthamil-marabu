"""தனிச்சொல் புணர்ச்சி — நூல் பெயரிட்டுக் கூறும் சொற்களுக்கு அதன் விதி (எழு. 209–432 இல் சொல்லுக்கெனக் கூறியவை).

    from senthamil_marabu.thanisol import punar_thani
    punar_thani("பனை", "காய்", "வேற்றுமை")     # பனங்காய் — எழு. 283 (ஐ கெட்டு அம்), 129 (அம்மின் மகரம் க முன் ங)

பொது விதியை (`punarchi.punar`) முந்தி இயங்குகிறது. நூல் இரு வழியைக் கூறுமிடத்து («உறழ்வே», «மிகினும் மானமில்லை», «உரித்தே»)
இரு வடிவும் வரும். விளைவு வடிவை நூல் எழுதாத இடத்தில் (பெரும்பாலும்) அது நூற்பாவின் சொற்படியே ஆக்கப்படுகிறது; காண்டிகை
ஒருதலை அன்மை எனக் குறித்த நூற்பாவால் வந்தது அந்நிலையோடே வரும்.
"""
from .punarchi import punar, to_oli, from_oli, INAM, VAL

N, O = "நூலில் நேரடியாக", "ஒருதலை அன்மை"
UYIR = "அஆஇஈஉஊஎஏஐஒஓஔ"


def _v(sol, sutra, vilakkam, nilai=N):
    return dict(sol=sol, vithi=[dict(id=sutra[0].split()[1], sutra=sutra, nilai=nilai, vilakkam=vilakkam, viruppu=False)], nilai=nilai)


def _mudhal(w):
    o = to_oli(w)
    return o[0] if o[0] in UYIR else o[:2]


def _val(w):
    m = _mudhal(w)
    return m[0] if len(m) == 2 and m[0] in VAL else None


def _mel(w):
    m = _mudhal(w)
    return len(m) == 2 and m[0] in "ஙஞணநமன"


def _uyir(w):
    return _mudhal(w) in UYIR


def _ol_last(w):
    o = to_oli(w)
    return o[-1]


def _cher(a, b):
    """எழுத்து நிலையில் நேர்ச் சேர்க்கை (மெய் + உயிர் → உயிர்மெய்)."""
    return from_oli(to_oli(a) + to_oli(b))


def _am(stem, varu, sutra, vilakkam):
    """அம் சாரியை: க ச த முன் இன மெல்லெழுத்து (எழு. 129); மெல்லினம் இடையினம் முன் மகரம் இல்லை (130); பிறவற்று முன் மகரம் நிற்கும்."""
    k = _val(varu)
    if k in ("க", "ச", "த"):
        return [_v(_cher(stem + INAM[k] + "்", varu), [sutra, "எழு. 129"], vilakkam + "; அம்மின் மகரம் " + INAM[k] + " ஆகும்")]
    if _mel(varu) or _mudhal(varu)[0] in "யரலவழள":
        return [_v(_cher(stem, varu), [sutra, "எழு. 130"], vilakkam + "; மெல்லினம் / இடையினம் வர மகரம் இல்லை")]
    return [_v(_cher(stem + "ம்", varu), [sutra], vilakkam)]


def _mel_migu(w, varu, sutra, vilakkam, nilai=N):
    k = _val(varu)
    return [_v(_cher(w + INAM[k] + "்", varu), [sutra], vilakkam, nilai)] if k else []


def _val_migu(w, varu, sutra, vilakkam, nilai=N):
    k = _val(varu)
    return [_v(_cher(w + k + "்", varu), [sutra], vilakkam, nilai)] if k else []


def _iyalbu(w, varu, sutra, vilakkam, nilai=N):
    return [_v(_cher(w, varu), [sutra], vilakkam, nilai)]


MARAM_MEL = {"உதி": "எழு. 243", "ஒடு": "எழு. 262", "சே": "எழு. 278", "விசை": "எழு. 282", "ஞெமை": "எழு. 282", "நமை": "எழு. 282"}


def punar_thani(a, b, vagai="அல்வழி", inam="பெயர்"):
    """நூல் தனி விதி கூறும் சொல்லெனில் அவ்விதியின் விளைவுகள்; இல்லையெனில் None."""
    R = []
    V = vagai == "வேற்றுமை"
    if a in ("பனை", "ஆவிரை"):
        if a == "பனை" and b == "அட்டு":
            return [_v("பனாட்டு", ["எழு. 284"], "பனையின் முன் அட்டு வர ஐ நில்லாது; ஆகாரம் வரும்")]
        return _am(a[:-1], b, "எழு. 283", "ஐ இறுதி கெட்டு மெய் நிற்க அம்மொடு சிவணும்")
    if a == "புளி":
        if inam == "மரப்பெயர்":
            return _am("புளிய", b, "எழு. 244", "புளிமரக் கிளவிக்கு அம் சாரியை (உடம்படுமெய் ய் — எழு. 140)")
        return _mel_migu(a, b, "எழு. 245", "ஏனைப் புளிப்பெயர் மெல்லெழுத்து மிகும்") + \
            _val_migu(a, b, "எழு. 246", "வல்லெழுத்து மிகினும் மானமில்லை")
    if a in ("பூல்", "வேல்", "ஆல்"):
        return _am(a[:-1], b, "எழு. 375", "பூல், வேல், ஆல் — அம் இடை வரும்")
    if a == "பீர்":
        return _am(a[:-1], b, "எழு. 365", "பீர் அம்மொடும் சிவணும்") + _mel_migu(a, b, "எழு. 363", "மெல்லெழுத்து மிகுதல்")
    if a in ("ஆர்", "வெதிர்", "சார்"):
        if a == "சார்" and b == "காழ்":
            return [_v("சார்க்காழ்", ["எழு. 364"], "சார் காழ்வயின் வலிக்கும்")]
        return _mel_migu(a, b, "எழு. 363", "ஆர், வெதிர், சார், பீர் — மெல்லெழுத்து மிகுதல் மெய் பெறத் தோன்றும்")
    if a == "குமிழ்" and inam == "மரப்பெயர்":
        return _am(a[:-1], b, "எழு. 386", "குமிழ் மரப்பெயர் பீரொடு ஓரியற்று — அம்") + _mel_migu(a, b, "எழு. 386", "பீரொடு ஓரியற்று — மெல்லெழுத்து")
    if a in MARAM_MEL and _val(b):
        return _mel_migu(a, b, MARAM_MEL[a], "உதிமர இயல் — மெல்லெழுத்து மிகும்")
    if a in ("யா", "பிடா", "தளா") and _val(b):
        return _mel_migu(a, b, "எழு. 229", "யா, பிடா, தளா — மெல்லெழுத்து மிகும்") + _val_migu(a, b, "எழு. 230", "வல்லெழுத்து மிகினும் மானமில்லை")
    if a in ("ஆ", "மா") and inam != "மரப்பெயர்":
        st = a + "ன்"
        out = punar(st, b, vagai)
        for o in out:
            o["vithi"] = [dict(id="231", sutra=["எழு. 231"], nilai=N, vilakkam=f"ஆவும் மாவும் னகரம் ஒற்றும்: {st}", viruppu=False)] + o["vithi"]
        return out
    if a == "நாழி" and b == "உரி":
        return [_v("நாடுரி", ["எழு. 240"], "உரி வர நாழியின் இறுதி இகரம் மெய்யொடும் கெட, டகரம் ஒற்றும்")]
    if a == "வேட்கை" and b == "அவா":
        return [_v("வேணவா", ["எழு. 288"], "செய்யுளில் — ஐ இறுதி மெய்யொடும் கெட, டகாரம் ணகாரமாகும்")]
    if a == "அகம்" and b == "கை":
        return [_v("அங்கை", ["எழு. 315"], "முதனிலை ஒழிய முன்னவை கெட, மெல்லெழுத்து மிகும்")] + punar(a, b, vagai)
    if a == "நும்" and _val(b):
        return [_v(_cher("நு" + INAM[_val(b)] + "்", b), ["எழு. 325"], "நும் — மெல்லெழுத்து மிகும்")]
    if a == "எகின்" and inam != "மரப்பெயர்" and _val(b):
        return [_v(_cher("எகின" + _val(b) + "்", b), ["எழு. 337"], "ஏனை எகின் — அகரம் வரும்; வல்லெழுத்து மிகும்")]
    if a == "தேன்":
        if b == "இறாஅல்":
            return [_v("தேனிறாஅல்", ["எழு. 343"], "இறாஅல் தோற்றம் இயற்கை"), _v("தேத்திறாஅல்", ["எழு. 344"], "ஒற்றுமிகு தகரமொடு நிற்றலும் உரித்து")]
        if _val(b):
            return (_iyalbu(a, b, "எழு. 340", "மேனிலை ஒத்தல் (இயல்பு)") + _val_migu("தே", b, "எழு. 340", "வல்லெழுத்து மிகும் — இறுதி இல்லை")
                    + _mel_migu("தே", b, "எழு. 341", "மெல்லெழுத்து மிகினும் மானமில்லை", O))
        if _mel(b):
            return _iyalbu(a, b, "எழு. 342", "மெல்லெழுத்து இயையின் இறுதியொடு உறழும்") + _iyalbu("தே", b, "எழு. 342", "இறுதி கெட")
    if a == "அழன்" and _val(b):
        return _val_migu("அழ", b, "எழு. 354", "அழன் இறுதி கெட வல்லெழுத்து மிகும்")
    if a == "முன்" and b == "இல்":
        return [_v("முற்றில்", ["எழு. 355"], "இல் மிசை றகரம் ஒற்றல் — தொல்லியல் மரபு")]
    if a in ("நெல்", "செல்", "கொல்", "சொல்") and _val(b) and not V:
        out = punar(a, b, "வேற்றுமை")
        for o in out:
            o["vithi"] = [dict(id="371", sutra=["எழு. 371"], nilai=N, vilakkam="அல்வழியிலும் வேற்றுமை இயல", viruppu=False)] + o["vithi"]
        return out
    if a in ("தாழ்", "தமிழ்") and _val(b):
        s = "எழு. 384" if a == "தாழ்" else "எழு. 385"
        nl = N if (a == "தாழ்" and b == "கோல்") else O
        return [_v(_cher(_cher(a, "அ") + _val(b) + "்", b), [s, "எழு. 128"],
                   "அக்கு இடை வரும்; வல்லெழுத்து வர அக்கின் இறுதி மெய்யொடும் கெடும்", nl)] + punar(a, b, vagai)
    if a == "பாழ்" and _val(b):
        return punar(a, b, vagai) + _mel_migu(a, b, "எழு. 387", "மெல்லெழுத்து உறழும்")
    if a == "கீழ்" and _val(b):
        return _val_migu(a, b, "எழு. 395", "உறழத் தோன்றும் — வல்லெழுத்து மிகுதல்") + _iyalbu(a, b, "எழு. 395", "உறழத் தோன்றும் — இயல்பு")
    if a in ("தான்", "பேன்", "கோன்", "குயின்"):
        return _iyalbu(a, b, "எழு. 351" if a != "குயின்" else "எழு. 335", "திரிபிடன் இல்லை — இயற்கை")
    if a == "தாய்":
        return _iyalbu(a, b, "எழு. 358", "தாய் இயற்கையாகும்")
    if a == "நீ" and _val(b):
        return _iyalbu(a, b, "எழு. 250", "நீ — வல்லெழுத்து இயற்கை")
    if a in ("ஆ", "மா", "யா") and _val(b) and inam != "மரப்பெயர்":
        return _iyalbu(a, b, "எழு. 224", "வல்லெழுத்து மிகாது — இயல்பு")
    if a == "பூ" and _val(b):
        return _iyalbu(a, b, "எழு. 268", "ஊ இறுதி இயல்பு (264) இல்லை") + _val_migu(a, b, "எழு. 268", "வல்லெழுத்து மிகுதலும் உரித்து")
    if a in ("வண்டு", "பெண்டு") and V:
        stem = from_oli(to_oli(a)[:-1])                              # குற்றியலுகரம் கெட — «வண்ட்»
        out = []
        for sar, sut, vil in [("இன்", "எழு. 420", "இன்னொடு சிவணும்")] + ([("அன்", "எழு. 421", "அன்னும் வரையார்")] if a == "பெண்டு" else []):
            for r in punar(_cher(stem, sar), b, "வேற்றுமை")[:1]:
                out.append(dict(sol=r["sol"], vithi=[dict(id=sut.split()[1], sutra=[sut], nilai=N, vilakkam=vil, viruppu=False)] + r["vithi"], nilai=r["nilai"]))
        return out
    if a == "சாவ":
        return [*punar(a, b, vagai), _v(_cher("சா" + (_val(b) + "்" if _val(b) else ""), b), ["எழு. 209"], "இறுதி வகரம் கெடுதலும் உரித்து")]
    if a == "வாழிய":
        return [*punar(a, b, vagai), _v(_cher("வாழி", b), ["எழு. 211"], "இறுதி அகரம் கெடுதலும் உரித்து")]

    # ── இரண்டாம் தொகுதி
    def gen(note_sutra, note, x=a, y=b, vg=vagai, im=inam, nilai=N):
        out = punar(x, y, vg, im, thani_vithi=False)
        for o in out:
            o["vithi"] = [dict(id=note_sutra.split()[1], sutra=[note_sutra], nilai=nilai, vilakkam=note, viruppu=False)] + o["vithi"]
            if nilai == O:
                o["nilai"] = O
        return out

    if a == "நிலா" and V:
        k = _val(b)
        return [_v(a + "த்து" + k + "்" + b if k else punar(a + "த்து", b, "வேற்றுமை", thani_vithi=False)[0]["sol"], ["எழு. 228", "எழு. 133"],
                   "நிலா அத்தொடு சிவணும்; அத்தின் முன் வல்லெழுத்து மிகும்")]
    if a in ("பனி", "வளி", "மழை", "வெயில்", "இருள்") and V:
        sut = {"பனி": "எழு. 241", "வளி": "எழு. 242", "மழை": "எழு. 287", "வெயில்": "எழு. 377", "இருள்": "எழு. 402"}[a]
        base = a if a[-1] in "்" else (a + "ய்" if _ol_last(a) in "இஈஐ" else a + "வ்")
        st1 = _cher(base, "அத்து")
        st2 = _cher(base, "இன்")
        k = _val(b)
        f1 = st1 + k + "்" + b if k else _cher(_cher(base, "அத்த்"), b)
        f2 = punar(st2, b, "வேற்றுமை", thani_vithi=False)[0]["sol"]
        return [_v(f1, [sut, "எழு. 241"], "காலப் பெயர் — வேற்றுமைக்கு அத்துச் சாரியை (பனியின் இயல்பு)"),
                _v(f2, [sut, "எழு. 241"], "காலப் பெயர் — வேற்றுமைக்கு இன் சாரியை (பனியின் இயல்பு)")]
    if a == "எரு":
        return _am("எருவ", b, "எழு. 260", "எரு அம்மொடு சிவணும் (உடம்படுமெய் வ்)")
    if a == "செரு" and _val(b):
        return [_v("செருவ" + _val(b) + "்" + b, ["எழு. 260"], "செரு — அம்மின் மகரம் கெட, தம் ஒற்று மிகும்")]
    if a in ("ஆடூஉ", "மகடூஉ"):
        return gen("எழு. 271", "இயல்பு") + [_v(punar(a + "வின்", b, "வேற்றுமை", thani_vithi=False)[0]["sol"], ["எழு. 271"], "இன் இடை வரினும் மானமில்லை")]
    if a == "ஏ":
        return [_v(punar("ஏஎ", b, vagai, inam, thani_vithi=False)[0]["sol"], ["எழு. 277"], "ஏ இறுதிக்கு எகரம் வரும்")]
    if a == "வெரிந்" and _val(b):
        return _mel_migu("வெரி", b, "எழு. 300", "இறுதி முழுதும் கெட மெல்லெழுத்து") + _val_migu("வெரி", b, "எழு. 301", "வல்லெழுத்து மிகுதலும் உரித்து")
    if a in ("ஆண்", "பெண்") and inam != "மரப்பெயர்":
        return gen("எழு. 303", "ஆண், பெண் — அஃறிணைப் பெயர் இயற்கை")
    if a == "விண்" and _val(b):
        return gen("எழு. 302", "பொது விதி") + [_v("விண்ணத்து" + _val(b) + "்" + b, ["எழு. 305", "எழு. 133"], "செய்யுளில் தொழில் வர அத்துச் சாரியை உண்மையும் உரித்து")]
    if a == "எண்" and not V and _val(b) and inam == "பெயர்":
        return gen("எழு. 308", "எண் (உணவுப் பெயர்) அல்வழியிலும் வேற்றுமை இயற்கை", vg="வேற்றுமை")
    if a == "முரண்" and _val(b):
        return gen("எழு. 309", "முரண் — தொழிற்பெயராயினும் முதலியல் (302)", im="பெயர்")
    if a == "இலம்" and b == "படு":
        return [_v("இலம்படு", ["எழு. 316"], "செய்யுளில் மகரம் நிற்றலும் உரித்து")] + punar(a, b, vagai, inam, thani_vithi=False)
    if a in ("ஈம்", "கம்", "உரும்", "மின்", "பின்", "பன்", "வல்", "புள்", "வள்") or (a == "கன்" and not V):
        sut = "எழு. 328" if a in ("ஈம்", "கம்", "உரும்") else "எழு. 345" if a in ("மின்", "பின்", "பன்", "கன்") else "எழு. 373" if a == "வல்" else "எழு. 403"
        return gen(sut, "தொழிற்பெயர் இயல", im="தொழிற்பெயர்")
    if a == "கன்" and V and _val(b):
        return [_v("கன்ன" + _val(b) + "்" + b, ["எழு. 346", "எழு. 337"], "வேற்றுமையில் ஏனை எகினொடு ஒக்கும் — அகரம் வரும்; வல்லெழுத்து மிகும்")]
    if a == "மீன்" and _val(b):
        return [_v(_cher(a, b), ["எழு. 339"], "வல்லெழுத்து உறழ்வு — இயல்பு")] + [_v("மீற்" + b, ["எழு. 339"], "வல்லெழுத்து உறழ்வு — றகரம்")]
    if a == "பொன்" and _val(b):
        return gen("எழு. 332", "பொது விதி") + _am("பொல", b, "எழு. 356", "செய்யுளில் ஈறு கெட லகாரமும் மகாரமும் தோன்றும்: பொலம்")
    if a == "இல்" and _val(b):
        k = _val(b)
        return [_v("இல்லை" + k + "்" + b, ["எழு. 372"], "இன்மை செப்பின் ஐ இடை வருதல் (வல்லெழுத்து மிகுதலோடு)"),
                _v("இல்லா" + k + "்" + b, ["எழு. 372"], "ஆகாரம் வருதல் (வல்லெழுத்து மிகுதலோடு)"),
                _v(_cher(a, b), ["எழு. 372"], "இயற்கை யாதல்")]
    if a == "மக்கள்" and _val(b) and not V:
        return gen("எழு. 398", "அல்வழி") + [_v("மக்கட்" + b, ["எழு. 404"], "தக்கவழி அறிந்து வலித்தலும் உரித்து", O)]
    if a == "உண்டு" and _val(b):
        return [_v("உள்" + b, ["எழு. 430"], "உண்மை செப்பின் இறுதி மெய்யொடும் கெட, மேனிலை ஒற்று ளகாரமாகும்")] + gen("எழு. 430", "இயல்பு")
    DISAI = {"வடக்கு": "வட", "தெற்கு": "தென்", "கிழக்கு": "கிழ", "மேற்கு": "மே"}
    if a in DISAI and b in DISAI:
        return [_v(DISAI[a] + b, ["எழு. 432"], "திரிபு வேறு கிளப்பின் ஒற்றும் உகரமும் கெடும்" + ("; தெற்கின் ஒற்று னகாரமாகும்" if a == "தெற்கு" else "")),
                _v(a[:-1] + "ே" + b, ["எழு. 431"], "இருதிசை புணரின் ஏ இடை வரும்")]
    if a == "இன்றி":
        return punar(a, b, vagai, inam, thani_vithi=False) + [_v(_cher("இன்று", b) if not _val(b) else "இன்று" + b, ["எழு. 237"], "செய்யுளில் இகரம் உகரமாதல் உரித்து")]
    if a == "யான்":
        return _iyalbu(a, b, "எழு. 353", "அல்வழியில் குறுகலும் திரிதலும் இல்லை") if not V else None
    if a == "கலம்" and _val(b):
        return [_v("கலத்து" + _val(b) + "்" + b, ["எழு. 168", "எழு. 133"], "கலம் என்னும் அளவுக்கு அத்து இடை வரும்")]
    return None
