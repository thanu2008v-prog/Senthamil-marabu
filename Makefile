PY ?= python3

validate:
	$(PY) scripts/validate.py
db:
	$(PY) scripts/build_db.py
bundle:
	$(PY) scripts/export_bundle.py
csv:
	$(PY) scripts/export_csv.py
all: validate db bundle csv
serve: all
	$(PY) -m http.server 8000
clean:
	rm -f build/senthamil.db build/bundle.json build/sutras.csv build/senthamil_v2.db build/bundle_v2.json build/sutras_v2.csv
.PHONY: validate db bundle csv all serve clean

# --- v2: நூல்மரபு வடிவம் (PLAN.md) ---
v2:
	$(PY) scripts/migrate_v2.py
nool-check:
	$(PY) scripts/check_nool.py
rules:
	$(PY) -m tests.test_mozhimarabu
nool:
	$(PY) scripts/build_nool.py
build-v2:
	$(PY) scripts/build_v2.py
yaml-import:
	$(PY) scripts/import_yaml.py
	$(PY) scripts/check_nool.py
sithaivu:
	$(PY) scripts/sithaivu.py
kuri:
	$(PY) kuriyaakkam/sothanai.py
	$(PY) orunguri/sothanai.py
	$(PY) orunguri/aavanam.py
pack:
	$(PY) scripts/pack_data.py
	$(PY) docs/make_docs.py
test:
	$(PY) -m pytest -q tests/test_api.py tests/test_punarchi.py tests/test_thanisol.py tests/test_en.py tests/test_en_adai.py tests/test_urupu.py tests/test_vinai.py tests/test_vili.py tests/test_pothu.py tests/test_adimaanam.py tests/test_isai_kanakku.py
sothanai:
	$(PY) scripts/build_sothanai.py
	$(PY) scripts/build_nunnarivu.py
site:
	$(PY) karuvi/build.py
	$(PY) scripts/build_site.py
	$(PY) scripts/build_seyali.py
punarchi:
	$(PY) scripts/build_punarchi.py
pothu:
	$(PY) scripts/build_pothu.py
	$(PY) scripts/build_maatteru.py
	$(PY) scripts/build_oppeedu_oli.py
	$(PY) scripts/build_oppeedu_maathirai.py
	$(PY) scripts/build_oppeedu_thinai.py
	$(PY) scripts/build_ennikkai.py
	$(PY) scripts/build_kaalam.py
	$(PY) scripts/build_oppeedu_isai.py
	$(PY) scripts/build_isai_sol.py
	$(PY) scripts/build_isai_kanakku.py
	$(PY) scripts/build_tharukkam.py
alavai:
	$(PY) scripts/build_alavai.py
kalanjiyam:
	$(PY) scripts/kalanjiyam.py
check: validate v2 sithaivu nool-check rules nool build-v2 kuri pack punarchi pothu test sothanai alavai site llm md kalanjiyam

.PHONY: sothanai md llm pothu punarchi alavai site kalanjiyam pack test kuri sithaivu v2 nool-check rules nool build-v2 yaml-import check book

urai-kit:
	python3 scripts/make_urai_kit.py
	cd build/urai_kit && python3 check_urai.py maathiri_othu04.json --othu ezhuthu:4

book: nool
	$(PY) scripts/build_book.py
llm:
	$(PY) scripts/build_llm_kit.py
md:
	$(PY) scripts/export_md.py
